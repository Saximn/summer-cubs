'use client';
import React, { useEffect, useState } from 'react';
import { Box, Grid, Stack,  FormGroup,  FormControlLabel,  Checkbox,  Button} from '@mui/material';
import PrivacyTipIcon from '@mui/icons-material/PrivacyTip';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import Card from '../_components/Card';

export default function PolicyPage() {
  const [chartData, setChartData] = useState<{ time: string; value: number }[]>([]);

  useEffect(() => {
    const fetchPrediction = async () => {
      try {
        const res = await fetch('http://127.0.0.1:5000/api/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ patients: 50 }), // you can make this dynamic
        });

        const data = await res.json();

        if (data.prediction) {
          const predictionArray = data.prediction.slice(0, 24);
          const formatted = predictionArray.map((val: number, idx: number) => ({
            time: `${String(idx).padStart(2, '0')}:00`,
            value: val < 0 ? 0 : Math.round(val),
          }));
          setChartData(formatted);
        }
      } catch (err) {
        console.error('Prediction fetch error:', err);
      }
    };

    fetchPrediction();
  }, []);

  return (
    <Box className="w-full h-full px-4 py-6 flex justify-center items-center">
      <Box className="flex flex-col gap-6 w-full max-w-[1075px]">
        {/* Top Section */}
        <Box className="bg-primary rounded p-6 shadow-md w-full">
          <h4 className="font-bold text-3xl text-white mb-4">Live Data Stream</h4>
          <Stack direction="row" spacing={3} className="overflow-x-auto">
            {[
              { title: 'EHR Event', subtitle: 'Patient #789 Admitted', time: '10:22:15' },
              { title: 'IoT Vital', subtitle: 'Low O₂ Sat (Bed 8)', time: '10:23:01' },
              { title: 'Staff Schedule', subtitle: 'Nurse Lee - Break', time: '10:25:33' },
            ].map((item, index) => (
              <Card key={index} className="flex flex-col  min-w-[300px] gap-3" color="white">
                <h6 className="font-bold">{item.title}</h6>
                <Card className="bg-navy h-20" color="#313860">
                  <Box sx={{ flexGrow: 1 }}>
                    <Grid container sx={{ color: 'orange' }}>
                      <Grid size={2}>
                        <PrivacyTipIcon />
                      </Grid>
                      <Grid size={10}>
                        <h6 className="font-bold text-white mb-1">{item.subtitle}</h6>
                        <h6 className="text-gray-500">{item.time}</h6>
                      </Grid>
                    </Grid>
                  </Box>
                </Card>
              </Card>
            ))}
          </Stack>
        </Box>

        {/* Bottom Section */}
        <Box className="flex flex-col md:flex-row gap-6 w-full">
          {/* Left Box */}
          <Box className="bg-primary rounded w-1/2 p-6">
            <h4 className="font-bold text-3xl text-white mb-4 ml-2">Policy Recommendations</h4>
            <p className="text-white ">
            <FormGroup>
              <FormControlLabel control={<Checkbox sx={{ color: 'white' }} />} label="Open 5 bed" />
              <FormControlLabel control={<Checkbox sx={{ color: 'white' }} />} label="Direct 2 nurse" />
            </FormGroup>
            </p>
            <Button
              className="top-30 bg-background rounded-full font-bold text-xs p-3 w-42 ml-38"
              variant="contained"
            >
              Implement
            </Button>
          </Box>

          {/* Right Box: Forecast Model */}
          <Box className="bg-primary rounded w-1/2 h-full p-6">
            <h4 className="font-bold text-3xl text-white mb-4 ml-2">Forecast Model</h4>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={chartData}>
                <XAxis dataKey="time" stroke="#fff" />
                <YAxis stroke="#fff" />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#82ca9d" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
