import torch
import torch.nn as nn

class MultiFeatureLSTM(nn.Module):
    def __init__(self, input_size, hidden_size=64, horizon=24):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc   = nn.Linear(hidden_size, horizon)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])