'use client'
import { Box,Stack,Button,Table,TableBody,TableCell,TableContainer,TableHead,TableRow,Paper } from '@mui/material';
import Card from '../_components/Card';

function createData(
  metric: string,
  before: string,
  after: string,
  change: string,
) {
  return { metric, before, after, change };
}

const rows = [
  createData('Room Availability', '30 unit', '40 unit', '33% increase'),
  createData('Queue Time', '60 minutes', '30 minutes', '50% decrease'),
  createData('Staff Availability', '20 unit', '12 unit', '40% decrease'),
];

export default function SimulationPage() {
  return (
    <Box className="w-full h-full px-4 py-6 flex justify-center items-center">
      <Box className="flex flex-col gap-6 w-full max-w-[1075px]">
        {/*Top Section*/}
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
              className="bg-background rounded-full font-bold text-xs px-6 py-2"
              variant="contained"
            >
              Run Simulation
            </Button>
          </Box>
        </Box>

        {/*Bottom Section*/}
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
