import { Box, FormControl, InputLabel, MenuItem, Select } from '@mui/material';
import React, { useState, useEffect } from 'react';

type Occupant = {
  id: string;
  name: string;
};

type Room = {
  room_number: string;
  capacity: number;
  floor: number;
  current_occupants: Occupant[];
};

type RoomDataGrid = {
  availableCount: number;
  rooms: Record<string, Room[]>;
};

type FloorAvailability = Record<number, number>;

export default function RoomAvailability() {
  const [selectedFloor, setSelectedFloor] = useState(1);
  const [roomData, setRoomData] = useState<RoomDataGrid>({
    availableCount: 0,
    rooms: {}
  });
  const [floorAvailability, setFloorAvailability] = useState<FloorAvailability>({});
  const [loading, setLoading] = useState(false);

  const floors = [1, 2, 3, 4, 5];
  const columns = [1, 2, 3, 4, 5, 6, 7];
  const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];

  useEffect(() => {
    const fetchAvailability = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/room/availability/`, {
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' }
        });
        if (!res.ok) throw new Error('Failed to fetch availability');
        const data = await res.json();
        setFloorAvailability(data);
      } catch (err) {
        console.error('Availability error:', err);
      }
    };
    fetchAvailability();
  }, []);

  useEffect(() => {
    const fetchRooms = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/room/floor/${selectedFloor}/`, {
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' }
        });
        if (!res.ok) throw new Error('Failed to fetch rooms');
        const rawRooms = await res.json();

        const grid: Record<string, Room[]> = {};
        let availableCount = 0;

        rawRooms.forEach((room: Room) => {
          const row = room.room_number[0];
          const col = parseInt(room.room_number.slice(1));
          if (!grid[row]) grid[row] = [];
          grid[row][col - 1] = room;

          if (room.current_occupants.length < room.capacity) availableCount++;
        });

        setRoomData({ availableCount, rooms: grid });
      } catch (err) {
        console.error('Room fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchRooms();
  }, [selectedFloor]);

  const getRoomStatus = (row: string, col: number) => {
    const room = roomData.rooms?.[row]?.[col - 1];
    return room ? room.current_occupants.length < room.capacity : false;
  };

  return (
    <Box>
      <h6 className="font-bold">Total Room Availability: {Object.values(floorAvailability).reduce((a, b) => a + b, 0)} units</h6>

      <div className="flex items-center justify-center my-2">
        <FormControl size="small" sx={{ backgroundColor: 'white', borderRadius: '10px' }}>
          <InputLabel id="select-floor-label">Floor</InputLabel>
          <Select
            labelId="select-floor-label"
            id="select-floor"
            value={selectedFloor}
            label="Floor"
            onChange={(e) => setSelectedFloor(Number(e.target.value))}
          >
            {floors.map((floor) => (
              <MenuItem key={floor} value={floor}>
                Floor {floor} ({floorAvailability[floor] ?? 0} available)
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </div>

      <Box className="flex items-center justify-center">
        <div className="w-[90%] grid grid-cols-8 gap-2">
          <div></div>
          {columns.map((col) => (
            <div key={col} className="flex items-center justify-center">
              <span className="text-teal-500 font-bold text-sm">{col}</span>
            </div>
          ))}

          {rows.map((row) => (
            <React.Fragment key={row}>
              <div className="flex items-center justify-center">
                <span className="text-teal-500 font-bold text-sm">{row}</span>
              </div>
              {columns.map((col) => (
                <div key={`${row}${col}`} className="flex items-center justify-center">
                  <button
                    className={`
                      w-full aspect-square rounded-md border-2 border-transparent
                      transition-all duration-200 ease-in-out
                      hover:scale-110 hover:border-white hover:shadow-lg
                      focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50
                      ${getRoomStatus(row, col)
                        ? 'bg-rose-400 hover:bg-rose-500'
                        : 'bg-gray-500 hover:bg-gray-600'}
                    `}
                    title={`Room ${row}${col} - ${getRoomStatus(row, col) ? 'Available' : 'Occupied'}`}
                    disabled
                  />
                </div>
              ))}
            </React.Fragment>
          ))}
        </div>
      </Box>
    </Box>
  );
}
