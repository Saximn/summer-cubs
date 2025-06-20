import { Box, Button } from "@mui/material";
import { useState } from "react";

export default function IotAlerts() {

    const [alertsData, setAlertsData] = useState([
        { id: 1, message: "Fall detected in Room 101", severity: "high", acknowledged: false },
        { id: 2, message: "Sepsis Risk Alert: Patient #789", severity: "medium", acknowledged: false },
        { id: 3, message: "Heart rate alert in Room 103", severity: "high", acknowledged: false },
        { id: 4, message: "Oxygen level low in Room 104", severity: "high", acknowledged: false },
        { id: 5, message: "Patient movement detected in Room 105", severity: "low", acknowledged: false },
    ]);

    const handleAcknowledge = (id: number) => {
        setAlertsData((prevAlerts) =>
            prevAlerts.map((alert) =>
                alert.id === id ? { ...alert, acknowledged: true } : alert
            )
        );
    };

    return (
        <Box className=" overflow-y-auto">
            {alertsData.map((alert) => (
                <Box
                    key={alert.id}
                    className={`p-1 py-2 mb-2 rounded ${
                        alert.acknowledged
                            ? 'bg-gray-200'
                            : alert.severity === 'high'
                            ? 'bg-red-100'
                            : alert.severity === 'medium'
                            ? 'bg-yellow-100'
                            : 'bg-green-100'
                    }`}
                >
                    <h6 className="font-bold ml-1">{alert.message}</h6>
                    <Button
                        variant="text"
                        className={`mt-1 ${
                            alert.acknowledged
                                ? 'text-gray-500'
                                :
                            alert.severity === 'high'
                                ? 'text-red-600'
                                : alert.severity === 'medium'
                                ? 'text-yellow-600'
                                : 'text-green-600'
                        }`}
                        size="small"
                        onClick={() => handleAcknowledge(alert.id)}
                        disabled={alert.acknowledged}
                    >
                        {alert.acknowledged ? "Acknowledged" : "Acknowledge"}
                    </Button>
                </Box>
            ))}
        </Box>
    );
}