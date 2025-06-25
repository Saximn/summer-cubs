import { useMemo, useState } from 'react';
import {
  MaterialReactTable,
  MRT_EditActionButtons,
  useMaterialReactTable,
  type MRT_ColumnDef,
  type MRT_TableOptions,
  type MRT_Row,
} from 'material-react-table';
import {
  Box,
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Tooltip,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

type Patient = {
  id: string;
  name: string;
  dob: string; // ISO string, e.g., "1999-12-31"
};

const PatientTable = () => {
  const [validationErrors, setValidationErrors] = useState<Record<string, string | undefined>>({});

  const columns = useMemo<MRT_ColumnDef<Patient>[]>(() => [
    {
      accessorKey: 'id',
      header: 'ID',
      enableEditing: false,
    },
    {
      accessorKey: 'name',
      header: 'Name',
      muiEditTextFieldProps: {
        required: true,
        error: !!validationErrors.name,
        helperText: validationErrors.name,
        onFocus: () => setValidationErrors({ ...validationErrors, name: undefined }),
      },
    },
    {
      accessorKey: 'dob',
      header: 'Date of Birth',
      muiEditTextFieldProps: {
        type: 'date',
        required: true,
        InputLabelProps: { shrink: true },
        error: !!validationErrors.dob,
        helperText: validationErrors.dob,
        onFocus: () => setValidationErrors({ ...validationErrors, dob: undefined }),
      },
    },
  ], [validationErrors]);

  const queryClient = useQueryClient();

  const { data = [], isFetching, isLoading, isError } = useQuery<Patient[]>({
    queryKey: ['patients'],
    queryFn: async () => {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/patient/`, {
        credentials: 'include',
      });
      return res.json();
    },
  });

  const createMutation = useMutation({
    mutationFn: async (patient: Partial<Patient>) => {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/patient/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(patient),
      });
      return res.json();
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['patients'] }),
  });

  const updateMutation = useMutation({
    mutationFn: async (patient: Patient) => {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/patient/${patient.id}/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(patient),
      });
      return res.json();
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['patients'] }),
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/patient/${id}/`, {
        method: 'DELETE',
        credentials: 'include',
      });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['patients'] }),
  });

  const handleCreate: MRT_TableOptions<Patient>['onCreatingRowSave'] = async ({ values, table }) => {
    if (!values.name || !values.dob) {
      setValidationErrors({
        name: !values.name ? 'Name is required' : undefined,
        dob: !values.dob ? 'Date of birth is required' : undefined,
      });
      return;
    }
    setValidationErrors({});
    await createMutation.mutateAsync(values);
    table.setCreatingRow(null);
  };

  const handleEdit: MRT_TableOptions<Patient>['onEditingRowSave'] = async ({ values, table }) => {
    setValidationErrors({});
    await updateMutation.mutateAsync(values);
    table.setEditingRow(null);
  };

  const handleDelete = (row: MRT_Row<Patient>) => {
    if (window.confirm('Are you sure you want to delete this patient?')) {
      deleteMutation.mutate(row.original.id);
    }
  };

  const table = useMaterialReactTable({
    columns,
    data,
    getRowId: (row) => row.id,
    createDisplayMode: 'modal',
    editDisplayMode: 'modal',
    enableEditing: true,
    onCreatingRowSave: handleCreate,
    onEditingRowSave: handleEdit,
    renderRowActions: ({ row, table }) => (
      <Box sx={{ display: 'flex', gap: '1rem' }}>
        <Tooltip title="Edit">
          <IconButton onClick={() => table.setEditingRow(row)}>
            <EditIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Delete">
          <IconButton color="error" onClick={() => handleDelete(row)}>
            <DeleteIcon />
          </IconButton>
        </Tooltip>
      </Box>
    ),
    renderTopToolbarCustomActions: ({ table }) => (
      <Button variant="contained" onClick={() => table.setCreatingRow(true)}>
        Add Patient
      </Button>
    ),
    state: {
      isLoading,
      isSaving: createMutation.isPending || updateMutation.isPending || deleteMutation.isPending,
      showAlertBanner: isError,
      showProgressBars: isFetching,
    },
    renderCreateRowDialogContent: ({ table, row, internalEditComponents }) => (
      <>
        <DialogTitle>Add Patient</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {internalEditComponents}
        </DialogContent>
        <DialogActions>
          <MRT_EditActionButtons table={table} row={row} />
        </DialogActions>
      </>
    ),
    renderEditRowDialogContent: ({ table, row, internalEditComponents }) => (
      <>
        <DialogTitle>Edit Patient</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {internalEditComponents}
        </DialogContent>
        <DialogActions>
          <MRT_EditActionButtons table={table} row={row} />
        </DialogActions>
      </>
    ),
    muiTablePaperProps: {
        sx: { width: '100%', height: '100%' }
      },
  });

  return <MaterialReactTable table={table} />;
};

export default PatientTable;
