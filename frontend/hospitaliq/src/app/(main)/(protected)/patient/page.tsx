"use client"

import { Box } from "@mui/material";
import PatientTable from "./_components/PatientTable";

export default function PatientPage() {
    return (
        <Box className="bg-primary rounded flex items-center justify-center h-[90vh] w-[90%] p-6">
            <PatientTable />
        </Box>
    )
}