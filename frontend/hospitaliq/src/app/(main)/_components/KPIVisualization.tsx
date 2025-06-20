import { Box } from "@mui/material";
import { LineChart } from "@mui/x-charts/LineChart";

export default function KPIVisualization() {

    const margin = { right: 24 };
    const RoomAvailabilityData = [25, 30, 28, 35, 40, 45, 50];
    const QueueTimeData = [5, 10, 15, 20, 25, 30, 35];
    const StaffAvailabilityData = [10, 12, 14, 16, 18, 20, 22];
    const xLabels = [
        '12:00',
        '13:00',
        '14:00',
        '15:00',
        '16:00',
        '17:00',
        '18:00'
    ];

    return (
        <Box className="h-full">
            <LineChart
            series={[
                { data: RoomAvailabilityData, label: 'Room Availability', valueFormatter: (v) => `${v}%`, showMark: false },
                { data: QueueTimeData, label: 'Queue Time', valueFormatter: (v) => `${v}%`, showMark: false },
                { data: StaffAvailabilityData, label: 'Staff Availability', valueFormatter: (v) => `${v}%`, showMark: false}
            ]}
            xAxis={[{ scaleType: 'point', data: xLabels }]}
            yAxis={[
                {
                width: 50,
                valueFormatter: (value) => `${value}%`
                }
            ]}
            margin={margin}
            />
        </Box>
    );
}