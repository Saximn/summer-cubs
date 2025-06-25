import { Box, FormControl, Grid, InputLabel, MenuItem, Select, Typography, Tooltip } from '@mui/material';
import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button
} from '@mui/material';
import { assignRoom } from './actions';

type Occupant = {
    id: string;
    name: string;
}

type Room = {
    room_number: string;
    capacity: number;
    floor: number;
    current_occupants: Occupant[];
}

type RoomDataGrid = {
    availableCount: number;
    rooms: Record<string, Room[]>;
}

export default function PickRoom({ selectedPatient }: { selectedPatient: any }) {

    const [confirmOpen, setConfirmOpen] = useState(false);
    const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);

    const [roomData, setRoomData] = useState<RoomDataGrid>({
        availableCount: 0,
        rooms: {}
    });

    const [loading, setLoading] = useState(false);


    const [selectedFloor, setSelectedFloor] = useState(1);

    type FloorAvailability = Record<number, number>;

    const [floorAvailability, setFloorAvailability] = useState<FloorAvailability>({});

    useEffect(() => {
        const fetchAvailability = async () => {
            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/room/availability/`, {
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (!res.ok) {
                    throw new Error('Failed to fetch availability data');
                }

                const data = await res.json();
                setFloorAvailability(data);
            } catch (error) {
                console.error('Error fetching availability data:', error);
            }
        }
        fetchAvailability();
    }, []);

    useEffect(() => {
        const fetchRoomData = async () => {
            setLoading(true);
            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/room/floor/${selectedFloor}/`, {
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                console.log(res);

                if (!res.ok) {
                    throw new Error('Failed to fetch room data');
                }
                const rawRooms = await res.json();

                const roomGrid: Record<string, Room[]> = {};
                let availableCount = 0;

                rawRooms.forEach((room: Room) => {
                    const row = room.room_number[0];
                    const col = parseInt(room.room_number.slice(1));

                    if (!roomGrid[row]) roomGrid[row] = [];

                    roomGrid[row][col - 1] = room;

                    if (room.current_occupants.length < room.capacity) {
                        availableCount++;
                    }
                });

                setRoomData({
                    availableCount,
                    rooms: roomGrid
                });
            } catch (error) {
                console.error('Error fetching room data:', error);
            } finally {
                setLoading(false);
            }
        }
        fetchRoomData();
    }, [selectedFloor]);



    const floors = [1, 2, 3, 4, 5];
    const columns = [1, 2, 3, 4, 5, 6, 7];
    const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];


    const getRoomData = (row: string, col: number) => {
        return roomData.rooms?.[row]?.[col - 1] ?? null;
    };

    const getRoomStatus = (row: string, col: number) => {
        const room = getRoomData(row, col);
        return room ? room.current_occupants.length < room.capacity : false;
    };

    const handleRoomClick = (row: string, col: number) => {
        const room = getRoomData(row, col);
        console.log(room)
        if (!room) return;

        const isFull = room.current_occupants.length >= room.capacity;
        if (isFull) {
            alert(`Room ${room.room_number} is full.`);
            return;
        }

        console.log(selectedPatient)
        setSelectedRoom(room);
        setConfirmOpen(true); // show confirmation dialog
    };

    const handleConfirm = async () => {
        if (!selectedRoom) return;
        try {
            await assignRoom(selectedPatient.id, selectedRoom.room_number, selectedFloor);
            alert(`Assigned ${selectedPatient.patient_name} to ${selectedRoom.room_number}.`);
            setConfirmOpen(false);
            setSelectedRoom(null);
            // Refresh room data
            setSelectedFloor(prev => prev);
        } catch (error) {
            console.error(error);
            alert('Failed to assign room.');
        }
    };

    const handleCancel = () => {
        setConfirmOpen(false);
        setSelectedRoom(null);
    };

    return (
        <Box>
            <Dialog open={confirmOpen} onClose={handleCancel}>
                <DialogTitle>Confirm Room Assignment</DialogTitle>
                <DialogContent>
                    <Typography>
                        Assign <strong>{selectedPatient?.patient_name}</strong> to{' '}
                        <strong>
                            Floor {selectedRoom?.floor}, Room {selectedRoom?.room_number}
                        </strong>
                        ?
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCancel} color="inherit">
                        Cancel
                    </Button>
                    <Button onClick={handleConfirm} variant="contained" color="primary">
                        Confirm
                    </Button>
                </DialogActions>
            </Dialog>
            {/* Floor Header */}
            <div className="flex my-2">
                <div className="relative">
                    <FormControl size='small' variant='filled' sx={{
                        backgroundColor: 'white',
                        borderRadius: '10px'
                    }}>
                        <InputLabel id="select-floor-label">Floor</InputLabel>
                        <Select
                            labelId="select-floor-label"
                            id="select-floor"
                            value={selectedFloor}
                            label="Floor"
                            onChange={(event) => setSelectedFloor(Number(event.target.value))}
                        >
                            {floors.map(floor => (
                                <MenuItem key={floor} value={floor}>
                                    Floor {floor} ({floorAvailability[floor] ?? 0} available)
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </div>
            </div>

            <Box className="flex items-center justify-center mt-6">
                {/* Grid Container */}
                <div className="w-full grid grid-cols-8 gap-2 bg-white p-4 rounded-lg pr-7">
                    {/* Empty top-left cell */}
                    <div></div>

                    {/* Column headers */}
                    {columns.map(col => (
                        <div key={col} className="flex items-center justify-center">
                            <span className="text-teal-500 font-bold text-sm">
                                {col}
                            </span>
                        </div>
                    ))}

                    {/* Grid rows */}
                    {rows.map(row => (
                        <React.Fragment key={row}>
                            {/* Row label */}
                            <div className="flex items-center justify-center">
                                <span className="text-teal-500 font-bold text-sm">
                                    {row}
                                </span>
                            </div>

                            {/* Room cells */}
                            {columns.map(col => (
                                <div key={`${row}${col}`} className="flex items-center justify-center">
                                    <Tooltip
                                        title={`Room ${row}${col} - ${getRoomStatus(row, col) ? 'Available' : 'Occupied'}`}
                                        arrow
                                        placement="top"
                                    >
                                        <button
                                            className={`
                        w-full aspect-square rounded-md border-2 border-transparent
                        transition-all duration-200 ease-in-out
                        hover:scale-110 hover:border-white hover:shadow-lg
                        focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50
                        ${getRoomStatus(row, col)
                                                    ? 'bg-rose-400 hover:bg-rose-500'
                                                    : 'bg-gray-500 hover:bg-gray-600'
                                                }
                                        `}
                                            onClick={() => handleRoomClick(row, col)}
                                        />
                                    </Tooltip>
                                </div>
                            ))}
                        </React.Fragment>
                    ))}
                </div>
            </Box>
        </Box>
    )
}