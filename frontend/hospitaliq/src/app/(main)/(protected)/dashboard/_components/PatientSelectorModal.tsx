// src/components/PatientSelectorModal.tsx

import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import { MaterialReactTable, type MRT_ColumnDef } from 'material-react-table';

type Patient = {
  id: string;
  name: string;
  dob: string;
};

type Props = {
  open: boolean;
  onClose: () => void;
  onSelect: (patient: Patient) => void;
};

export default function PatientSelectorModal({ open, onClose, onSelect }: Props) {
  const [search, setSearch] = useState('');

  const { data: patients = [], isLoading } = useQuery<Patient[]>({
    queryKey: ['patients'],
    queryFn: async () => {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/patient/`, {
        credentials: 'include',
      });
      return res.json();
    },
    enabled: open, // only fetch if modal is open
  });

  const filteredPatients = useMemo(() => {
    return patients.filter(p =>
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.dob.includes(search)
    );
  }, [search, patients]);

  const columns = useMemo<MRT_ColumnDef<Patient>[]>(() => [
    { accessorKey: 'name', header: 'Name' },
    { accessorKey: 'dob', header: 'Date of Birth' },
  ], []);

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>Select Patient</DialogTitle>
      <DialogContent>
        <TextField
          placeholder="Search by name or DOB"
          variant="outlined"
          fullWidth
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          sx={{ mb: 2 }}
        />
        <MaterialReactTable
          columns={columns}
          data={filteredPatients}
          enableRowActions
          enableTopToolbar={false}
          enableBottomToolbar={false}
          state={{ isLoading }}
          renderRowActions={({ row }) => (
            <Button variant="outlined" onClick={() => {
              onSelect(row.original);
              onClose();
            }}>
              Select
            </Button>
          )}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} variant="text">Cancel</Button>
      </DialogActions>
    </Dialog>
  );
}
