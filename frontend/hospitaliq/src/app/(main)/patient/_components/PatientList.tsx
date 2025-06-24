import { Box, List, ListItem, ListItemText } from "@mui/material";

export default function PatientList({ selectedPatient, setSelectedPatient }: { selectedPatient: any, setSelectedPatient: (patient: any) => void }) {
    return (
        <Box>
            <List
                sx={{
                    width: '100%',
                    maxHeight: '100%',
                    overflowY: 'auto',
                    bgcolor: 'background.paper',
                    borderRadius: '10px',
                    boxShadow: 1,
                }}
                component="ol"
            >
                {Array.from({ length: 10 }, (_, index) => (
                    <ListItem
                        key={index}
                        divider={index !== 9}
                        sx={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            padding: 1,
                        }}
                    >
                        <ListItemText primary={`Patient ${index + 1}`} />
                        <ListItemText secondary={`Room ${index + 1}`} />
                    </ListItem>
                ))}
            </List>
        </Box>
    );
}