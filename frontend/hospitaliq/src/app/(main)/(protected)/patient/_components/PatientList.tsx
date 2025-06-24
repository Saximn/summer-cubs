import { Box, List, ListItem, ListItemText } from "@mui/material";

export default function PatientList({ selectedPatient, setSelectedPatient }: { selectedPatient: any, setSelectedPatient: (patient: any) => void }) {
    return (
        <Box className="rounded w-full flex flex-col min-h-0">
            <List
                sx={{
                  width: '100%',
                  bgcolor: 'background.paper',
                  overflow: 'auto',
                  flex: 1,
                  minHeight: 0,
                  borderRadius: '10px'
                }}
            >
                {Array.from({ length: 10 }, (_, index) => {
                    const patient = { id: index, name: `Patient ${index + 1}`, room: `Room ${index + 1}`, severity: index % 3 === 0 ? 'Critical' : index % 3 === 1 ? 'Severe' : 'Moderate', entry_time: `2024-06-01 10:0${index}` };
                    const isSelected = selectedPatient && selectedPatient.id === patient.id;
                    return (
                        <ListItem
                            component="button"
                            key={patient.id}
                            sx={{
                                display: 'list-item',
                                bgcolor: isSelected ? 'primary.light' : 'background.paper',
                                cursor: 'pointer',
                                width: '100%',
                                textAlign: 'left',
                                p: 2,
                                '&:hover': {
                                    bgcolor: 'primary.main',
                                    color: 'white',
                                },
                            }}
                            onClick={() => setSelectedPatient(patient)}
                        >
                            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                                <ListItemText
                                    primary={patient.name}
                                    slotProps={{
                                        primary: { fontSize: 18, fontWeight: 'bold' }
                                    }}
                                />
                                <ListItemText
                                    secondary={patient.room}
                                    slotProps={{
                                        secondary: { fontSize: 16 }
                                    }}
                                    sx={{ textAlign: 'right' }}
                                />
                            </Box>
                            <Box display="flex" justifyContent="space-between">
                                <ListItemText
                                    secondary={`Severity: ${patient.severity ?? 'Moderate'}`}
                                    slotProps={{
                                        secondary: { fontSize: 14 }
                                    }}
                                />
                                <ListItemText
                                    secondary={`Entry: ${patient.entry_time ?? '2024-06-01 10:00'}`}
                                    slotProps={{
                                        secondary: { fontSize: 14 }
                                    }}
                                    sx={{ textAlign: 'right' }}
                                />
                            </Box>
                        </ListItem>
                    );
                })}
            </List>
        </Box>
    );
}