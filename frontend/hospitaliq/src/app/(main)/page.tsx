'use client';
import { Box, Grid, Stack } from '@mui/material';


import React from 'react';

interface CardProps extends React.PropsWithChildren<{}> {
  className?: string;
}

const Card: React.FC<CardProps> = ({ children, className }) => (
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
    {children}
  </Box>
)

export default function Home() {
  return (
    <Box className="bg-primary rounded flex items-center justify-center h-[90%] w-[90%] p-6">
      <Grid className="w-full h-full" container spacing={3}>
        <Grid size={8}>
          <Stack spacing={3} className='h-full w-full'>
            <Stack direction='row' spacing={3} className='h-full w-full'>
              <Card className='flex flex-col gap-3'>
                <h6 className='font-bold'>Patients: 15</h6>
                <Card className='bg-primary flex-1'>

                </Card>
              </Card>
              <Card>Test 2</Card>
            </Stack>
            <Card>Test</Card>
          </Stack>
        </Grid>
        <Grid size={4}>
          <Stack spacing={3} className='h-full w-full'>
            <Card>Test</Card>
            <Card>Test</Card>
            <Card>Test</Card>
          </Stack>
        </Grid>
      </Grid>
    </Box>
  );
}