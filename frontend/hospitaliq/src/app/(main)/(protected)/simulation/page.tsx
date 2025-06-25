'use client';
import { useState } from 'react';
import {  Box,  Stack,  Button,  Table,  TableBody,  TableCell,  TableContainer,  TableHead,  TableRow,  Paper} from '@mui/material';
import Card from '../_components/Card';

interface RowData {
  metric: string;
  before: string;
  after: string;
  change: string;
}

export default function SimulationPage() {
  const [rows, setRows] = useState<RowData[]>([
    {
      metric: 'Patient Prediction',
      before: '-',
      after: '-',
      change: 'N/A',
    },
    {
      metric: 'Queue Time',
      before: '60 minutes',
      after: '30 minutes',
      change: '50% decrease',
    },
    {
      metric: 'Staff Availability',
      before: '20 unit',
      after: '12 unit',
      change: '40% decrease',
    },
  ]);

  const handleRunSimulation = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patients: 50 }), // Replace with dynamic slider value if needed
    });

    const data = await response.json();

    if (data.error) {
      console.error('Prediction error:', data.error);
      return;
    }

    const prediction = data.prediction; // array of 24 values
    const predictedValue = Math.round(prediction[0]);
    const originalValue = 7; // You can make this dynamic too
    const diff = predictedValue - originalValue;
    const changePercent = ((diff / originalValue) * 100).toFixed(1);
    const changeLabel = diff >= 0
      ? `${changePercent}% increase`
      : `${Math.abs(Number(changePercent)).toFixed(1)}% decrease`;

    // Update the table rows
    setRows([
      {
        metric: 'Patient Prediction',
        before: `${originalValue} unit`,
        after: `${predictedValue} unit`,
        change: changeLabel,
      },
      {
        metric: 'Queue Time',
        before: '60 minutes',
        after: '30 minutes',
        change: '50% decrease',
      },
      {
        metric: 'Staff Availability',
        before: '20 unit',
        after: '12 unit',
        change: '40% decrease',
      },
    ]);
  } catch (error) {
    console.error('Error calling API:', error);
  }
};

  return (
    <Box className="w-full h-full px-4 py-6 flex justify-center items-center">
      <Box className="flex flex-col gap-6 w-full max-w-[1075px]">

        {/* Top Section */}
        <Box className="bg-primary rounded p-6 shadow-md w-full">
          <h4 className="font-bold text-3xl text-white mb-4">Simulation Sliders</h4>
          <Stack direction="row" spacing={3} className="overflow-x-auto">
            <Card className="flex flex-col gap-3 min-w-[300px]" color="white">
              <h6 className="font-bold">Bed Slider</h6>
            </Card>
            <Card className="flex flex-col gap-3 min-w-[300px]" color="white">
              <h6 className="font-bold">Staff Slider</h6>
            </Card>
            <Card className="flex flex-col gap-3 min-w-[300px]" color="white">
              <h6 className="font-bold">Patient Slider</h6>
            </Card>
          </Stack>
          <Box className="w-full flex justify-center mt-6">
            <Button
  onClick={handleRunSimulation}
  className="bg-background rounded-full font-bold text-xs px-6 py-2"
  variant="contained"
>
  Run Simulation
</Button>

          </Box>
        </Box>

        {/* Bottom Section */}
        <Box className="bg-primary rounded p-6 shadow-md w-full">
          <h4 className="font-bold text-3xl text-white mb-4">Results</h4>
          <TableContainer component={Paper}>
            <Table sx={{ minWidth: 600 }} aria-label="results table">
              <TableHead>
                <TableRow>
                  <TableCell>Metric</TableCell>
                  <TableCell align="right">Before</TableCell>
                  <TableCell align="right">After</TableCell>
                  <TableCell align="right">Change</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.metric}>
                    <TableCell component="th" scope="row">{row.metric}</TableCell>
                    <TableCell align="right">{row.before}</TableCell>
                    <TableCell align="right">{row.after}</TableCell>
                    <TableCell align="right">{row.change}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      </Box>
    </Box>
  );
}
