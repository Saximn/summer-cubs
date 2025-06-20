import { TextField, Select, MenuItem, SelectChangeEvent, FormControl, InputLabel, Button, Stack } from '@mui/material';
import React from 'react';
import CustomCard from './CustomCard';

export default function AddPatient() {

    const [severity, setSeverity] = React.useState('');
    const [name, setName] = React.useState('');

    return (
        <CustomCard className='bg-primary flex-1'>
            <h6 className='text-white font-bold'>Add Patient</h6>
            <Stack spacing={2} className='w-full h-full mt-2 items-center'>
                <TextField 
                    id="filled-basic" 
                    label="Name" 
                    variant="filled" 
                    sx={{
                        backgroundColor: 'white',
                        borderRadius: '10px',
                        width: '100%',
                    }}
                    slotProps={{
                        input: {
                            disableUnderline: true,
                        }
                    }}
                    value={name}
                    onChange={(event) => setName(event.target.value)}    
                />
                <FormControl variant='filled' fullWidth sx={{
                    backgroundColor: 'white',
                    borderRadius: '10px'
                }}>
                    <InputLabel id="select-severity-label">Severity</InputLabel>
                    <Select
                        labelId="select-severity-label"
                        id="select-severity"
                        value={severity}
                        label="Severity"
                        onChange={(event: SelectChangeEvent) => setSeverity(event.target.value)}
                        disableUnderline
                    >
                        <MenuItem value="low">Low</MenuItem>
                        <MenuItem value="medium">Medium</MenuItem>
                        <MenuItem value="high">High</MenuItem>
                    </Select>
                </FormControl>
                <Button className="bg-secondary rounded-full w-2/3" variant="contained">Add to List</Button>
            </Stack>
        </CustomCard>
    )
}