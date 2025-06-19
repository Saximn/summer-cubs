import { Box, Grid, Stack, FormGroup, FormControlLabel, Checkbox, Button, FormControl, RadioGroup, Radio } from "@mui/material"
import { RadarChart } from '@mui/x-charts/RadarChart';
import React from "react";
import PrivacyTipIcon from '@mui/icons-material/PrivacyTip';

interface CardProps extends React.PropsWithChildren<{}> {
  className?: string;
  color?: string;
}

const Card: React.FC<CardProps>= ({children, className, color}) => (
    <>
        <Box
            className={className}
            
            sx={{
            backgroundColor: color,
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
        </Box>
    </>
)

export default function PolicyPage() {
    return (
        <>
            <Box className="absolute top-[60px] bg-primary rounded flex items-center justify-center h-[350px] w-[1075px] p-9">
                <Box className="flex flex-col items-start justify-start w-full h-full">
                    <h4 className="font-bold text-3xl text-white mb-4">Live Data Stream</h4>
                </Box>
                <Grid className="absolute top-25 w-250 h-50 " container spacing={2}>
                    <Grid size={14}>
                        <Stack direction='row' spacing={3} className='h-full w-full'>
                            <Card className='flex flex-col gap-3' color='white'>
                                <h6 className='font-bold'>EHR Event</h6>
                                <Card className="bg-navy h-20" color='#313860'>
                                    <Box sx={{ flexGrow: 1 }}>
                                        <Grid container sx={{ color: 'orange' }}>
                                            <Grid size={2}>
                                                <PrivacyTipIcon />
                                            </Grid>
                                            <Grid size={8}>
                                                <h6 className='font-bold text-white mb-1'>Patient #789 Admitted</h6>
                                                <h6 className='text-gray-500'>10:22:15</h6>

                                            </Grid>
                                        </Grid>
                                    </Box>
                                </Card>
                            </Card>
                            <Card className='flex flex-col gap-3' color='white'>
                                <h6 className='font-bold'>IoT Vital</h6>
                                <Card className="bg-navy h-20" color='#313860'>
                                    <Box sx={{ flexGrow: 1 }}>
                                        <Grid container sx={{ color: 'orange' }}>
                                            <Grid size={2}>
                                                <PrivacyTipIcon />
                                            </Grid>
                                            <Grid size={8}>
                                                <h6 className='font-bold text-white mb-1'>Low O₂ Sat (Bed 8)</h6>
                                                <h6 className='text-gray-500'>10:23:01</h6>

                                            </Grid>
                                        </Grid>
                                    </Box>
                                </Card>
                            </Card>
                            <Card className='flex flex-col gap-3' color='white'>
                                <h6 className='font-bold'>Staff Schedule</h6>
                                <Card className="bg-navy h-20" color='#313860'>
                                    <Box sx={{ flexGrow: 1 }}>
                                        <Grid container sx={{ color: 'orange' }}>
                                            <Grid size={2}>
                                                <PrivacyTipIcon />
                                            </Grid>
                                            <Grid size={8}>
                                                <h6 className='font-bold text-white mb-1'>Nurse Lee - Break</h6>
                                                <h6 className='text-gray-500'>10:25:33</h6>

                                            </Grid>
                                        </Grid>
                                    </Box>
                                </Card>
                            </Card>
                        </Stack>
                    </Grid>
                </Grid>
            </Box>
            
            <Box className="absolute bottom-[60px] flex flex-row gap-6 w-[1075px] h-[350px]">
                <Box className="bg-primary rounded w-1/2 h-full p-6">
                        <h4 className="font-bold text-3xl text-white mb-4 ml-2">Policy Recommendations</h4>
                        <p className="text-white ">
                            <FormGroup>
                                <FormControlLabel control={<Checkbox sx={{ color: "white"}}/>} label="Open 5 bed" />
                                <FormControlLabel control={<Checkbox sx={{ color: "white"}}/>} label="Direct 2 nurse" />
                            </FormGroup>
                        </p>
                        <Button className="top-30 bg-background rounded-full font-bold text-xs p-3 w-42 ml-38" variant="contained">Implement</Button>
                </Box>
                <Box className="bg-primary rounded w-1/2 h-full p-6">
                    <h4 className="font-bold text-3xl text-white mb-4 ml-2">Forecast Model</h4>
                        <p className="text-white ">
                            <FormControl>
      <RadioGroup
        row
        aria-labelledby="demo-row-radio-buttons-group-label"
        name="row-radio-buttons-group"
        className="mb-2"
      >
        <FormControlLabel value="1h" control={<Radio sx={{
    color: "white"}}/>} label="1h" />
        <FormControlLabel value="24h" control={<Radio sx={{
    color: "white"}} />} label="24h" />
        <FormControlLabel value="7d" control={<Radio sx={{
    color: "white"}} />} label="7d" />
      </RadioGroup>
    </FormControl>
                        </p>
                        <Card color="white" className="h-50">
                        <RadarChart
      height={200}
      series={[{ data: [120, 98, 86, 99, 85] }]}
      radar={{
        max: 120,
        metrics: ['Patient Admitted', 'Room Availability', 'Staff Availability', 'Queue Time', 'IoT Alerts'],
      }}
    />
    </Card>
                </Box>
            </Box>
  
        </>
    )
}