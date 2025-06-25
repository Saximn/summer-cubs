export async function assignRoom(patientId: string, room_number: string, floor: number) {
    const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/patient_entry/${patientId}/assign_room/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ assigned_room: 
            {
                room_number,
                floor
            }
         }),
        credentials: 'include'
    });

    if (!res.ok) {
        throw new Error('Failed to assign room');
    }

    return res.json();
}