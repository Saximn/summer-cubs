'use server'

import { cookies } from 'next/headers';
import { loginToDjango } from "@/lib/auth/login";

import { User } from '@/lib/types/user';

export async function loginAction(formData: FormData) {
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;

    let user: User | null = null;
    let token: string | null = null;

    try {
        const result = await loginToDjango(email, password);
        user = result.user;
        token = result.token;


        // Store user information and token in cookies
        const cookieStore = await cookies();
        cookieStore.set('auth_token', token, {
            httpOnly: true,
            secure: true, // Use secure cookies in production
            sameSite: 'none',
            path: '/', // Set the path to root so it's accessible throughout the app
            maxAge: 60 * 60 * 24 * 7, // 1 week,
        });
        
        return { success: true, role: user.role };
    } catch (error) {
        console.error("Login failed:", error);
        return { success: false, error: "Invalid email or password" };
    }
}