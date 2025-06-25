'use client';

import { Box, FormControl, InputLabel, MenuItem, Select, Tooltip, Typography, Dialog, DialogTitle, DialogContent, DialogActions, Button } from '@mui/material';
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { assignRoom } from './actions';

type Occupant = { id: string; name: string; };
type Room = { room_number: string; capacity: number; floor: number; current_occupants: Occupant[]; };
type RoomDataGrid = { availableCount: number; rooms: Record<string, Room[]>; };
const floors = [1, 2, 3, 4, 5];
const columns = [1, 2, 3, 4, 5, 6, 7];
const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];

export default function PickRoom({ selectedPatient }: { selectedPatient: any }) {
    const [selectedFloor, setSelectedFloor] = useState(1);
    const [confirmOpen, setConfirmOpen] = useState(false);
    const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);

    const queryClient = useQueryClient();

    // Fetch floor availability
    const { data: floorAvailability = {}, isLoading: loadingAvailability } = useQuery({
        queryKey: ['floorAvailability'],
        queryFn: async () => {
            const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/room/availability/`, { credentials: 'include' });
            if (!res.ok) throw new Error('Failed to fetch floor availability');
            return res.json();
        }
    });

    // Fetch room data by floor
    const { data: roomData = { availableCount: 0, rooms: {} }, isLoading: loadingRooms } = useQuery({
        queryKey: ['rooms', selectedFloor],
        queryFn: async (): Promise<RoomDataGrid> => {
            const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/room/floor/${selectedFloor}/`, {
                credentials: 'include',
            });
            if (!res.ok) throw new Error('Failed to fetch room data');
            const rawRooms: Room[] = await res.json();

            const roomGrid: Record<string, Room[]> = {};
            let availableCount = 0;

            rawRooms.forEach((room) => {
                const row = room.room_number[0];
                const col = parseInt(room.room_number.slice(1));
                if (!roomGrid[row]) roomGrid[row] = [];
                roomGrid[row][col - 1] = room;
                if (room.current_occupants.length < room.capacity) availableCount++;
            });

            return { rooms: roomGrid, availableCount };
        }
    });

    const mutation = useMutation({
        mutationFn: ({ patientId, room_number, floor }: { patientId: string; room_number: string; floor: number }) =>
            assignRoom(patientId, room_number, floor),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['rooms', selectedFloor] });
            queryClient.invalidateQueries({ queryKey: ['floorAvailability'] });
            queryClient.invalidateQueries({ queryKey: ['incomplete-patient-entries']});
        }
    });

    const handleRoomClick = (row: string, col: number) => {
        const room = roomData.rooms?.[row]?.[col - 1];
        if (!room) return;
        const isFull = room.current_occupants.length >= room.capacity;
        if (isFull) return alert(`Room ${room.room_number} is full`);
        setSelectedRoom(room);
        setConfirmOpen(true);
    };

    const handleConfirm = async () => {
        if (!selectedRoom) return;
        try {
            await mutation.mutateAsync({
                patientId: selectedPatient.id,
                room_number: selectedRoom.room_number,
                floor: selectedRoom.floor
            });
            alert(`Assigned ${selectedPatient.patient_name} to ${selectedRoom.room_number}`);
            setConfirmOpen(false);
            setSelectedRoom(null);
        } catch {
            alert('Failed to assign room');
        }
    };

    const getRoomStatus = (row: string, col: number) => {
        const room = roomData.rooms?.[row]?.[col - 1];
        return room ? room.current_occupants.length < room.capacity : false;
    };

    return (
        <Box>
            {/* Confirm Dialog */}
            <Dialog open={confirmOpen} onClose={() => setConfirmOpen(false)}>
                <DialogTitle>Confirm Room Assignment</DialogTitle>
                <DialogContent>
                    <Typography>
                        Assign <strong>{selectedPatient?.patient_name}</strong> to{' '}
                        <strong>Floor {selectedRoom?.floor}, Room {selectedRoom?.room_number}</strong>?
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setConfirmOpen(false)}>Cancel</Button>
                    <Button onClick={handleConfirm} variant="contained">Confirm</Button>
                </DialogActions>
            </Dialog>

            {/* Floor Selector */}
            <Box className="flex my-2">
                <FormControl size="small" variant="filled" sx={{ backgroundColor: 'white', borderRadius: '10px' }}>
                    <InputLabel>Floor</InputLabel>
                    <Select value={selectedFloor} onChange={(e) => setSelectedFloor(Number(e.target.value))}>
                        {floors.map(floor => (
                            <MenuItem key={floor} value={floor}>
                                Floor {floor} ({floorAvailability[floor] ?? 0} available)
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
            </Box>

            {/* Room Grid */}
            <Box className="flex items-center justify-center mt-6">
                <div className="w-full grid grid-cols-8 gap-2 bg-white p-4 rounded-lg pr-7">
                    <div></div>
                    {columns.map(col => (
                        <div key={col} className="flex items-center justify-center">
                            <span className="text-teal-500 font-bold text-sm">{col}</span>
                        </div>
                    ))}
                    {rows.map(row => (
                        <React.Fragment key={row}>
                            <div className="flex items-center justify-center">
                                <span className="text-teal-500 font-bold text-sm">{row}</span>
                            </div>
                            {columns.map(col => (
                                <div key={`${row}${col}`} className="flex items-center justify-center">
                                    <Tooltip title={`Room ${row}${col} - ${getRoomStatus(row, col) ? 'Available' : 'Occupied'}`} arrow>
                                        <button
                                            onClick={() => handleRoomClick(row, col)}
                                            className={`
                        w-full aspect-square rounded-md border-2 border-transparent
                        transition-all duration-200 ease-in-out
                        hover:scale-110 hover:border-white hover:shadow-lg
                        focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50
                        ${getRoomStatus(row, col)
                                                    ? 'bg-rose-400 hover:bg-rose-500'
                                                    : 'bg-gray-500 hover:bg-gray-600'}
                      `}
                                        />
                                    </Tooltip>
                                </div>
                            ))}
                        </React.Fragment>
                    ))}
                </div>
            </Box>
        </Box>
    );
}
