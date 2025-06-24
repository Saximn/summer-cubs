'use server';

import { registerToDjango } from '@/lib/auth/register';

export async function registerAction(formData: FormData) {
  const email = formData.get('email') as string;
  const password = formData.get('password') as string;
  const fullname = formData.get('fullname') as string;
  const birthday = formData.get('birthday') as string; // format "YYYY-MM-DD"

  try {
    await registerToDjango(email, password, fullname, birthday);
    return { success: true };
  } catch (error) {
    console.error('Registration error:', error);

    if (error instanceof Response) {
        const res = await error.json();
        return { success: false, error: res }
    }

    return { success: false, error: { general : ['Someething went wrong. Please try again later.'] } };
  }
}
