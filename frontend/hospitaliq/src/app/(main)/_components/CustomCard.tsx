import React from 'react';
import { Box } from '@mui/material';

interface CardProps extends React.PropsWithChildren<{}> {
    className?: string;
}

export default function CustomCard({ children, className }: CardProps) {
    return (
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
}