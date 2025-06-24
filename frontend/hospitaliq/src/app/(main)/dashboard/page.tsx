'use client';
import { Box, Grid, Stack, List, ListItem, ListItemText } from '@mui/material';


import React from 'react';
import AddPatient from './_components/AddPatient';
import CustomCard from './_components/CustomCard';
import RoomAvailability from './_components/RoomAvailability';
import IotAlerts from './_components/IotAlerts';
import KPIVisualization from './_components/KPIVisualization';


export default function Home() {
  const formatTime = (num: number) => num.toString().padStart(2, '0');
  const [time, setTime] = React.useState({
    hours: 0,
    minutes: 30,
    seconds: 0,
  });
  return (
    <Box className="bg-primary rounded flex items-center justify-center h-[90vh] w-[90%] p-6">
      <Grid className="w-full h-full" container spacing={3}>
        <Grid className="h-full" size={8}>
          <Stack spacing={3} className='h-full w-full'>
            <Stack direction='row' spacing={3} className='h-full w-full'>
              <CustomCard className='flex flex-col gap-3'>
                <h6 className='font-bold'>Patients: 15</h6>
                <AddPatient />
              </CustomCard>
              <CustomCard>
                <RoomAvailability />
              </CustomCard>
            </Stack>
            <CustomCard className='min-h-0 flex flex-col'>
              <h6 className='font-bold'>KPI Visualization</h6>
              <KPIVisualization />
            </CustomCard>
          </Stack>
        </Grid>
        <Grid className='h-full' size={4}>
          <Stack spacing={3} className='h-full w-full'>
            <CustomCard className='min-h-0 flex flex-col'>
              <h6 className='font-bold'>Staff Availability: 24</h6>
                <List
                sx={{
                  width: '100%',
                  maxWidth: 360,
                  bgcolor: 'background.paper',
                  overflow: 'auto',
                  flex: 1,
                  minHeight: 0,
                  listStyleType: 'decimal',
                  pl: 3,
                }}
                component="ol"
                dense
                >
                {
                  Array.from({ length: 10 }, (_, index) => (
                  <ListItem
                    key={index}
                    sx={{ display: 'list-item', pl: 1 }}
                  >
                    <Box className='flex flex-row justify-between w-full'>
                      
                    <ListItemText sx={{
                      '.MuiTypography-root': {
                        fontWeight: 'bold',
                      }
                    }} >Staff Member {index + 1}</ListItemText>
                    <ListItemText sx={{
                      '.MuiTypography-root': {
                        fontWeight: 'normal',
                        textAlign: 'right',
                      }
                    }} >Available</ListItemText>
                    </Box>
                  </ListItem>
                  ))
                }
                </List>

            </CustomCard>
            <CustomCard className='min-h-0 flex flex-col'>
              <h6 className='font-bold'>Queue Time: 30 minutes</h6>
              <div className="flex flex-1 justify-center items-center gap-3">
              {/* Hours */}
              <div className="text-center">
                <div className="bg-cyan-400 text-white rounded-xl p-4 min-w-20 shadow-lg">
                  <div className="text-4xl font-bold leading-none">
                    {formatTime(time.hours)}
                  </div>
                </div>
                <div className="text-xs text-gray-500 mt-2">Hours</div>
              </div>
            
              
              {/* Minutes */}
              <div className="text-center">
                <div className="bg-cyan-400 text-white rounded-xl p-4 min-w-20 shadow-lg">
                  <div className="text-4xl font-bold leading-none">
                    {formatTime(time.minutes)}
                  </div>
                </div>
                <div className="text-xs text-gray-500 mt-2">Minutes</div>
              </div>
              
              
              {/* Seconds */}
              <div className="text-center">
                <div className="bg-cyan-400 text-white rounded-xl p-4 min-w-20 shadow-lg">
                  <div className="text-4xl font-bold leading-none">
                    {formatTime(time.seconds)}
                  </div>
                </div>
                <div className="text-xs text-gray-500 mt-2">Seconds</div>
              </div>
            </div>
          </CustomCard>
          <CustomCard className='min-h-0 flex flex-col'>
            <h6 className='font-bold'>IoT Alerts</h6>
            <IotAlerts />
          </CustomCard>
        </Stack>
      </Grid>
    </Grid>
    </Box >
  );
}