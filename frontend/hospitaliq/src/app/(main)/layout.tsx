import React from 'react';
import Navbar from "./_components/Navbar";
import { Box } from '@mui/material';

export default function MainLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
            <Navbar />
            <Box component="main" sx={{ flexGrow: 1, padding: 3 }}> 
                {children}
            </Box>
        </Box>
    )
}