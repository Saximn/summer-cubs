import React from 'react';
import Navbar from "./(protected)/_components/Navbar";
import { Box } from '@mui/material';
import { getCurrentUser } from '@/lib/auth/getCurrentUser';
import ReactQueryProvider from './_components/ReactQueryProvider';
import AccountMenu from './_components/AccountMenu';

export default async function MainLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {

    const user = await getCurrentUser()
    return (
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
            {user.role === 'medical_staff' ? <Navbar user={user} /> : <AccountMenu user={user} />}
            <Box component="main" sx={{ flexGrow: 1, padding: 3, alignItems: 'center', justifyContent: 'center', display: 'flex' }}>
                <ReactQueryProvider>
                    {children}
                </ReactQueryProvider>
            </Box>
        </Box>
    )
}