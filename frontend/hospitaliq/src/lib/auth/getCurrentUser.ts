import { cookies } from "next/headers";
import { cache } from "react";

export async function getCurrentUser() {
    const cookieStore = await cookies();
    const token = cookieStore.get('auth_token')?.value;
    if (!token) {
        return null; // No user is logged in
    }

    try {
        const response = await fetch(`${process.env.BACKEND_URL}/user/me`, {
            method: 'GET',
            headers: {
                Authorization: `Token ${token}`,
            },
            cache: 'no-store'
        });
        
        if (!response.ok) return null;
        
        return await response.json();
    } catch (error) {
        console.error("Failed to fetch current user:", error);
        return null; // Handle error gracefully
    }
}