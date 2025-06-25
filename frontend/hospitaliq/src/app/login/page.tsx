"use client";
import { Box, Stack, TextField, Button, Link } from '@mui/material'
import React, { useState } from 'react'
import { loginAction } from './actions'
import { useRouter } from 'next/navigation';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleLogin = async () => {
    const formData = new FormData();
    formData.append('email', email);
    formData.append('password', password)

    const result = await loginAction(formData);
    if (result.error) {
      setError(result.error);
    } else {
      // Redirect based on user role
      if (result.role === 'medical_staff') {
        router.push('/dashboard');
      } else {
        router.push('/patient');
      }
    }
  }

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
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <h6 className='font-bold'>Password</h6>
            <TextField
              className='bg-white rounded-lg'
              id="outlined-Text"
              placeholder='password'
              variant="outlined"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            {error && (
              <p className="text-red-600 text-xs">
                {error}
              </p>
            )}
            <Button
              className="bg-white rounded-full font-bold text-xs p-3 w-30 ml-45 text-blue-950"
              variant="contained"
              onClick={handleLogin}
            >
              Login
            </Button>

            <Box display="flex" justifyContent="center">
              <span className="text-xs text-gray-600 mr-1">Don't have an account yet?</span>
              <Link href="/register" underline="hover" className="text-xs font-bold text-blue-900">
                Register
              </Link>
            </Box>
          </Stack>
        </Box>
      </div>
    </div>
  )
}

export default LoginPage;