import { Box, List, ListItem, ListItemText, Button } from "@mui/material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export default function PatientList({
  selectedPatient,
  setSelectedPatient,
}: {
  selectedPatient: any;
  setSelectedPatient: (patient: any) => void;
}) {
  const queryClient = useQueryClient();

  const { data: patients = [], isLoading, isError } = useQuery({
    queryKey: ["incomplete-patient-entries"],
    queryFn: async () => {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/patient_entry/incomplete/`, {
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to fetch");
      return res.json();
    },
  });

  const dischargeMutation = useMutation({
    mutationFn: async (patientEntryId: string) => {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/patient_entry/${patientEntryId}/`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            exit_time: new Date().toISOString(),
            completed: true,
          }),
        }
      );
      if (!res.ok) throw new Error("Failed to discharge patient");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries(["incomplete-patient-entries"]);
    },
  });

  if (isLoading) return <Box>Loading patients...</Box>;
  if (isError) return <Box>Error loading patients.</Box>;

  return (
    <Box className="rounded w-full flex flex-col min-h-0">
      <List
        sx={{
          width: "100%",
          bgcolor: "background.paper",
          overflow: "auto",
          flex: 1,
          minHeight: 0,
          borderRadius: "10px",
        }}
      >
        {patients.map((patient: any) => {
          const isSelected = selectedPatient && selectedPatient.id === patient.id;
          return (
            <ListItem
              component="div"
              key={patient.id}
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "stretch",
                bgcolor: isSelected ? "primary.light" : "background.paper",
                cursor: "pointer",
                width: "100%",
                textAlign: "left",
                p: 2,
                "&:hover": {
                  bgcolor: "primary.main",
                  color: "white",
                },
              }}
              onClick={() => setSelectedPatient(patient)}
            >
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <ListItemText
                  primary={patient.patient_name || "Unknown"}
                  slotProps={{
                    primary: { style: { fontSize: 18, fontWeight: "bold" } },
                  }}
                />
                <ListItemText
                  secondary={patient.assigned_room ? `Floor ${patient.floor} Room ${patient.room_number}` : "Unallocated"}
                  slotProps={{
                    secondary: { style: { fontSize: 16 } },
                  }}
                  sx={{ textAlign: "right" }}
                />
              </Box>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <ListItemText
                  secondary={`Severity: ${patient.severity ?? "Unknown"}`}
                  slotProps={{
                    secondary: { style: { fontSize: 14 } },
                  }}
                />
                <ListItemText
                  secondary={`Entry: ${new Date(patient.entry_time).toLocaleString()}`}
                  slotProps={{
                    secondary: { style: { fontSize: 14 } },
                  }}
                  sx={{ textAlign: "right" }}
                />
              </Box>
              <Box display="flex" justifyContent="flex-end">
                <Button
                  variant="outlined"
                  color="error"
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation(); // Prevent selecting patient
                    dischargeMutation.mutate(patient.id);
                  }}
                >
                  Discharge
                </Button>
              </Box>
            </ListItem>
          );
        })}
      </List>
    </Box>
  );
}
