import { User } from '@/lib/types/user';

export async function loginToDjango(email: string, password: string): Promise<{user: User ; token: string}> {
    const response = await fetch(`${process.env.BACKEND_URL}/login/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
        throw new Error('Login failed');
    }

    const data = await response.json();
    return { user: data.user, token: data.token };
}   