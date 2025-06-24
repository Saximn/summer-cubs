"use client";

import { Box, Grid } from "@mui/material";
import PickRoom from "./_components/PickRoom";
import PatientList from "./_components/PatientList";
import React from "react";

export default function PatientPage() {
    const [selectedPatient, setSelectedPatient] = React.useState(null);
    return (
        <Box className="bg-primary rounded flex items-center justify-center h-[90vh] w-[90%] p-6">
            <Grid className="w-full h-full" container spacing={3}>
                <Grid size={6} className="flex flex-col h-full">
                    <h6 className="text-white text-2xl font-bold mb-4">Patient List</h6>
                    <PatientList selectedPatient={selectedPatient} setSelectedPatient={setSelectedPatient} />
                </Grid>
                <Grid size={6} className='h-full'>
                    <h6 className="text-white text-2xl font-bold mb-4">Slot</h6>
                    <PickRoom />
                </Grid>
            </Grid>
        </Box>
    )
}