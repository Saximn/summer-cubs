"use server"

export async function assignRoom(patientId: string, roomId: string) {
    "use server";
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/patientEntry/${patientId}/assign-room`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ room: roomId }),
    });

    if (!res.ok) {
        throw new Error('Failed to assign room');
    }

    return res.json();
}