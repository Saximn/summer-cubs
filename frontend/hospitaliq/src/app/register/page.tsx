"use client";

import { Box, Stack, TextField, Button, Link } from '@mui/material'
import React from 'react'
import { registerAction } from './actions';

const RegisterPage = () => {
    const [email, setEmail] = React.useState('');
    const [password, setPassword] = React.useState('');
    const [fullname, setfullname] = React.useState('');
    const [birthdate, setBirthdate] = React.useState('');
    const [error, setError] = React.useState<{
        email?: string[];
        password?: string[];
        fullname?: string[];
        birthdate?: string[];
        general?: string[]
     }>({});

    const handleRegister = async () => {
        const formData = new FormData();
        formData.append('email', email);
        formData.append('password', password);
        formData.append('fullname', fullname);
        formData.append('birthdate', birthdate);

        const result = await registerAction(formData);
        if (result.error) {
            setError(result.error);
        } else {
            // Redirect to login or dashboard based on user role
            window.location.href = '/login';
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
                        <h6 className='font-bold'>Full Name</h6>
                        <TextField
                            className='bg-white rounded-lg'
                            id="register-fullname"
                            placeholder='Your full name'
                            variant="outlined"
                            value={fullname}
                            onChange={(e) => setfullname(e.target.value)}
                            error = {Boolean(error.fullname)}
                            helperText={error.fullname?.[0]}
                            required
                        />
                        <h6 className='font-bold'>Email</h6>
                        <TextField
                            className='bg-white rounded-lg'
                            id="register-email"
                            placeholder='username@gmail.com'
                            variant="outlined"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            error = {Boolean(error.email)}
                            helperText={error.email?.[0]}
                            required
                        />
                        <h6 className='font-bold'>Password</h6>
                        <TextField
                            className='bg-white rounded-lg'
                            id="register-password"
                            placeholder='password'
                            type="password"
                            variant="outlined"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            error = {Boolean(error.password)}
                            helperText={error.password?.[0]}
                            required
                        />
                        <h6 className='font-bold'>Birthdate</h6>
                        <TextField
                            className='bg-white rounded-lg'
                            id="register-birthdate"
                            type="date"
                            variant="outlined"
                            value={birthdate}
                            onChange={(e) => setBirthdate(e.target.value)}
                            error = {Boolean(error.birthdate)}
                            helperText={error.birthdate?.[0]}
                            required
                        />
                        {error.general && (
                            <p className="text-red-600 text-xs">
                                {error.general[0]}
                            </p>
                        )}
                        <Button
                            className="bg-white rounded-full font-bold text-xs p-3 w-30 ml-45 text-blue-950"
                            variant="contained"
                            onClick={handleRegister}
                        >
                            Register
                        </Button>
                        <Box display="flex" justifyContent="center">
                            <span className="text-xs text-gray-600 mr-1">Already have an account?</span>
                            <Link href="/login" underline="hover" className="text-xs font-bold text-blue-900">
                                Login
                            </Link>
                        </Box>
                    </Stack>
                </Box>
            </div>
        </div>
    )
}

export default RegisterPage;