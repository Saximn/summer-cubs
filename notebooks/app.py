from flask_cors import CORS
from flask import Flask, request, jsonify
import torch
import numpy as np
import pickle
import pandas as pd
from model import MultiFeatureLSTM  # Replace with your actual model class


app = Flask(__name__)
CORS(app)

# Load the model architecture and weights
model = MultiFeatureLSTM(input_size=7, hidden_size=64, horizon=24)  # Adjust input_size if needed
model.load_state_dict(torch.load('model.pt', map_location=torch.device('cpu')))
model.eval()

# Load the scaler
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

# Hardcoded data for the last 167 hours (replace with DB fetch if needed)
hardcoded_data = [50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53, 50, 48, 52, 49, 51, 50, 47, 53]  # Example data

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        # Get the last hour's patients data from the request
        data = request.json
        last_hour_patients = data.get('patients', 0)

        # Combine the hardcoded data with the last hour's data
        # Make sure we always have exactly 168 values
        recent_data = hardcoded_data[-167:] if len(hardcoded_data) >= 167 else hardcoded_data
        while len(recent_data) < 167:
            recent_data.insert(0, recent_data[0])  # pad with oldest value

        input_counts = recent_data + [last_hour_patients]  # now exactly 168
        # Generate time-based features for the last 168 hours
        timestamps = pd.date_range(end=pd.Timestamp.now(), periods=168, freq='H')
        df_features = pd.DataFrame({'count': input_counts, 'ts': timestamps})
        df_features['hour'] = df_features['ts'].dt.hour
        df_features['day_of_week'] = df_features['ts'].dt.dayofweek
        df_features['day_of_year'] = df_features['ts'].dt.dayofyear

        # Add cyclical encodings
        df_features['sin_hour'] = np.sin(2 * np.pi * df_features['hour'] / 24)
        df_features['cos_hour'] = np.cos(2 * np.pi * df_features['hour'] / 24)
        df_features['sin_dow'] = np.sin(2 * np.pi * df_features['day_of_week'] / 7)
        df_features['cos_dow'] = np.cos(2 * np.pi * df_features['day_of_week'] / 7)
        df_features['sin_doy'] = np.sin(2 * np.pi * df_features['day_of_year'] / 365.25)
        df_features['cos_doy'] = np.cos(2 * np.pi * df_features['day_of_year'] / 365.25)

        # Select features and scale
        feature_cols = ["count", "sin_hour", "cos_hour", "sin_dow", "cos_dow", "sin_doy", "cos_doy"]
        scaled_data = scaler.transform(df_features[feature_cols])
        input_tensor = torch.tensor(scaled_data, dtype=torch.float32).unsqueeze(0)  # Shape: (1, 168, 7)

        # Make prediction
        with torch.no_grad():
            scaled_prediction = model(input_tensor).numpy()  # Shape: (1, 24)

        # Inverse transform the "count" feature
        count_min, count_max = scaler.data_min_[0], scaler.data_max_[0]
        prediction = scaled_prediction * (count_max - count_min) + count_min

        # Return the prediction
        return jsonify({'prediction': prediction.flatten().tolist()})

    except Exception as e:
        print("ERROR:", e)  # <--- Add this line
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)