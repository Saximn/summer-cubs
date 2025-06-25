import { Box, FormControl, Grid, InputLabel, MenuItem, Select, Typography, Tooltip } from '@mui/material';
import React, { useState } from 'react';

export default function PickRoom({ selectedPatient }: { selectedPatient: any }) {

    const [selectedFloor, setSelectedFloor] = useState(1);
    type RoomRows = string;
    type RoomData = {
        availableCount: number;
        rooms: Record<RoomRows, boolean[]>;
    };
    const roomData: Record<number, RoomData> = {
        1: {
            availableCount: 48,
            rooms: {
                A: [false, true, true, true, false, false, false],
                B: [true, true, true, true, true, true, true],
                C: [true, true, true, false, false, false, false],
                D: [true, false, false, true, true, true, false],
                E: [false, true, true, true, true, true, true],
                F: [false, true, true, true, false, false, true],
                G: [false, false, true, true, false, false, false]
            }
        },
        2: {
            availableCount: 35,
            rooms: {
                A: [true, false, true, false, true, false, true],
                B: [false, true, false, true, false, true, false],
                C: [true, true, false, false, true, true, false],
                D: [false, false, true, true, false, false, true],
                E: [true, false, false, true, true, false, true],
                F: [true, true, true, false, false, true, false],
                G: [false, true, true, true, false, false, true]
            }
        }
    };

    const floors = [1, 2, 3, 4, 5];
    const columns = [1, 2, 3, 4, 5, 6, 7];
    const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];

    const currentFloorData = roomData[selectedFloor] || { availableCount: 0, rooms: {} };

    const getRoomStatus = (row: RoomRows, col: number) => {
        if (!currentFloorData.rooms[row]) return false;
        return currentFloorData.rooms[row][col - 1] || false;
    };

    return (
        <Box>
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
                                    Floor {floor} ({roomData[floor]?.availableCount ?? 0} available)
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