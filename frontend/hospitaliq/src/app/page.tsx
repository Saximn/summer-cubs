import { Box, Stack, TextField, Button, Link } from '@mui/material'
import React from 'react'

const page = () => {
  return (
    <div className="relative w-full h-screen flex items-center justify-center bg-white">
      <img
        src="/bg.png"
        alt="Background"
        className="absolute top-0 left-0 w-full h-full object-cover z-0"
      />
      <div className="relative z-10 flex flex-col items-center">
        <img src="/logo-full.png" alt="HospitalIQ Logo" className="h-40" />

        <Box sx={{ width: '100%' }}>
      <Stack spacing={2}>
        <h6 className='font-bold'>Email</h6>
        <TextField
        className='bg-white rounded-lg'
          id="outlined-Text"
          placeholder='username@gmail.com'
          variant="outlined"
        />
        <h6 className='font-bold'>Password</h6>
        <TextField
        className='bg-white rounded-lg'
          id="outlined-Text"
          placeholder='password'
          variant="outlined"
        />
        <a href="/dashboard">
        <Button className="bg-white rounded-full font-bold text-xs p-3 w-30 ml-45 text-blue-950" variant="contained">Login</Button></a>
        
      </Stack>
    </Box>
      </div>
    </div>
  )
}

export default page