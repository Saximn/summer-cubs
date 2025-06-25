import { TextField, Select, MenuItem, SelectChangeEvent, FormControl, InputLabel, Button, Stack, Box, Typography, Chip, Avatar } from '@mui/material';
import { PersonAdd, Person, CalendarToday } from '@mui/icons-material';
import React from 'react';
import CustomCard from './CustomCard';
import PatientSelectorModal from './PatientSelectorModal'

export default function AddPatient() {

    const [selectedPatient, setSelectedPatient] = React.useState<any>(null);
    const [severity, setSeverity] = React.useState('');
    const [modalOpen, setModalOpen] = React.useState(false);

    const handleSubmit = async () => {
        if (!selectedPatient || !severity) return;
        console.log(selectedPatient.id)
        await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/patient_entry/`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient: selectedPatient.id,
                severity,
            }),
        });
        setSelectedPatient(null);
        setSeverity('');
    };

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'low': return 'success';
            case 'medium': return 'warning';
            case 'high': return 'error';
            default: return 'default';
        }
    };

    return (
        <CustomCard className="bg-primary flex-1">
            <h6 className="text-white font-bold">Add Patient Entry</h6>
            <Stack spacing={3} className="w-full h-full mt-4 items-center">
                
                {/* Patient Selection */}
                <Box className="w-full">
                    {selectedPatient ? (
                        <Box 
                            sx={{ 
                                bgcolor: 'white', 
                                borderRadius: '12px', 
                                p: 2,
                                border: '2px solid transparent',
                                '&:hover': { 
                                    border: '2px solid #1976d2',
                                    cursor: 'pointer'
                                }
                            }}
                            onClick={() => setModalOpen(true)}
                        >
                            <Box display="flex" alignItems="center" gap={2}>
                                <Box flex={1}>
                                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#1976d2' }}>
                                        {selectedPatient.name}
                                    </Typography>
                                    <Box display="flex" alignItems="center" gap={1}>
                                        <CalendarToday sx={{ fontSize: 16, color: '#666' }} />
                                        <Typography variant="body2" color="text.secondary">
                                            DOB: {selectedPatient.dob}
                                        </Typography>
                                    </Box>
                                </Box>
                                <Button 
                                    variant="outlined" 
                                    size="small"
                                    sx={{ 
                                        minWidth: 'auto',
                                        borderRadius: '8px'
                                    }}
                                >
                                    Change
                                </Button>
                            </Box>
                        </Box>
                    ) : (
                        <Button 
                            variant="outlined" 
                            onClick={() => setModalOpen(true)} 
                            sx={{ 
                                bgcolor: 'white', 
                                width: '100%',
                                height: '80px',
                                borderRadius: '12px',
                                border: '2px dashed #ccc',
                                '&:hover': {
                                    border: '2px dashed #1976d2',
                                    bgcolor: '#f5f5f5'
                                }
                            }}
                            startIcon={<PersonAdd />}
                        >
                            <Box textAlign="center">
                                <Typography variant="body1" sx={{ fontWeight: 500 }}>
                                    Select Patient
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Click to choose from patient list
                                </Typography>
                            </Box>
                        </Button>
                    )}
                </Box>

                {/* Severity Selection */}
                <Box className="w-full">
                    <FormControl variant='filled' fullWidth sx={{ backgroundColor: 'white', borderRadius: '12px' }}>
                        <InputLabel id="select-severity-label">Severity</InputLabel>
                        <Select
                            labelId="select-severity-label"
                            id="select-severity"
                            value={severity}
                            label="Severity"
                            onChange={(event) => setSeverity(event.target.value)}
                            sx={{ borderRadius: '12px' }}
                        >
                            <MenuItem value="low">
                                <Box display="flex" alignItems="center" gap={1}>
                                    <Chip label="Low" color="success" size="small" />
                                    <Typography>Low Priority</Typography>
                                </Box>
                            </MenuItem>
                            <MenuItem value="medium">
                                <Box display="flex" alignItems="center" gap={1}>
                                    <Chip label="Medium" color="warning" size="small" />
                                    <Typography>Medium Priority</Typography>
                                </Box>
                            </MenuItem>
                            <MenuItem value="high">
                                <Box display="flex" alignItems="center" gap={1}>
                                    <Chip label="High" color="error" size="small" />
                                    <Typography>High Priority</Typography>
                                </Box>
                            </MenuItem>
                        </Select>
                    </FormControl>
                </Box>

                {/* Submit Button */}
                <Button
                    className="bg-secondary rounded-full w-2/3 mt-4"
                    variant="contained"
                    onClick={handleSubmit}
                    disabled={!selectedPatient || !severity}
                    sx={{ 
                        height: '48px',
                        fontWeight: 600,
                        fontSize: '16px',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                        '&:hover': {
                            boxShadow: '0 6px 16px rgba(0,0,0,0.2)',
                        },
                        '&:disabled': {
                            bgcolor: '#ccc',
                            color: '#666'
                        }
                    }}
                >
                    Add to List
                </Button>
            </Stack>

            <PatientSelectorModal
                open={modalOpen}
                onClose={() => setModalOpen(false)}
                onSelect={(patient) => setSelectedPatient(patient)}
            />
        </CustomCard>
    )
}