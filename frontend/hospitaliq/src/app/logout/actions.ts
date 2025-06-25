'use server';

import { cookies } from 'next/headers';
import { logoutFromDjango } from '@/lib/auth/logout';
import { redirect } from 'next/navigation';

export async function logoutAction() {
    const cookieStore = await cookies();
    const token = cookieStore.get('auth_token')?.value;

    if (token) {
        await logoutFromDjango(token);
    }

    // Clear the auth_token cookie
    cookieStore.delete('auth_token');

    redirect('/login');
}