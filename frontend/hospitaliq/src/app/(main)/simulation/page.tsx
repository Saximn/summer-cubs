'use client'
import { Box, Grid, Stack, Button, Slider, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, lighten } from '@mui/material';
import { grey } from '@mui/material/colors';

interface CardProps extends React.PropsWithChildren<{}> {
  className?: string;
}

const marks = [
  {
    value: 0,
    label: '0',
  },
  {
    value: 1,
    label: '',
  },
  {
    value: 2,
    label: '2',
  },
  {
    value: 3,
    label: '',
  },
  {
    value: 4,
    label: '4',
  },
  {
    value: 5,
    label: '',
  },
  {
    value: 6,
    label: '6',
  },
  {
    value: 7,
    label: '',
  },
  {
    value: 8,
    label: '8',
  },
  {
    value: 9,
    label: '',
  },
  {
    value: 10,
    label: '10',
  },
];

function valuetext(value: number) {
  return `${value}`;
}

const DiscreteSliderLabel = () => (
    <Slider
        aria-label="Always visible"
        defaultValue={5}
        getAriaValueText={valuetext}
        step={1}
        marks={marks}
        valueLabelDisplay="on"
        min={0}
        max={10}
        sx={{
        color: 'navy',
      '& .MuiSlider-markLabel': {
        fontWeight: 'bold', 
        fontSize: 15, 
        color: 'gray'
      },
      '& .MuiSlider-thumb': {
        backgroundColor: 'white',
        border: '1px solid navy',
      },
    }}
      />
)

const Card: React.FC<CardProps>= ({children, className}) => (
    <>
        <Box
            className={className}
            sx={{
            backgroundColor: 'white',
            borderRadius: '10px',
            padding: '16px',
            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
            height: '100%',
            width: '100%',
            }}
        >
            <Box sx={{ marginBottom: '40px' }}>
                {children}
            </Box>
            {className === 'flex flex-col gap-3' ?
            <DiscreteSliderLabel/> : null }
        </Box>
    </>
)

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
        <>
            <Box className="absolute top-[60px] bg-primary rounded flex items-center justify-center h-[350px] w-[1075px] p-9 ">
                <Grid className="absolute top-8 w-250 h-50 " container spacing={2}>
                    <Grid size={14}>
                        <Stack direction='row' spacing={3} className='h-full w-full'>
                            <Card className='flex flex-col gap-3'>
                            <h6 className='font-bold'>Bed Slider</h6>
                            </Card>
                            <Card className='flex flex-col gap-3'>
                                <h6 className='font-bold'>Staff Slider</h6>
                            </Card>
                            <Card className='flex flex-col gap-3'>
                                <h6 className='font-bold'>Patient Slider</h6>
                            </Card>
                        </Stack>
                    </Grid>
                </Grid>
                <Button className="top-30 bg-background rounded-full font-bold text-xs p-3 w-42" variant="contained">Run Simulation</Button>
            </Box>
            <Box className="absolute bottom-[60px] bg-primary rounded flex items-center justify-center h-[350px] w-[1075px] p-9 ">
                <Box className="flex flex-col items-start justify-start w-full h-full">
                    <h4 className="font-bold text-3xl text-white mb-4">Results</h4>
                    <TableContainer component={Paper}>
                        <Table sx={{ minWidth: 600 }} aria-label="simple table">
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
                                    <TableRow
                                        key={row.metric}
                                        sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                    >
                                    <TableCell component="th" scope="row">
                                        {row.metric}
                                    </TableCell>
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
        </>
    )
}