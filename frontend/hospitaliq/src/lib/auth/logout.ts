'use server'

import { cookies } from 'next/headers';

export async function logoutFromDjango(token: string) {
    try {
        // Optionally, you can make a request to the backend to invalidate the token
        await fetch(`${process.env.BACKEND_URL}/logout/`, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`,
            },
        });
    } catch (error) {
        console.error("Logout failed:", error);
        return { success: false, error: "Logout failed" };
    }
}