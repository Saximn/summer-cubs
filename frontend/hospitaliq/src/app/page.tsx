// app/page.tsx
import { getCurrentUser } from '@/lib/auth/getCurrentUser';
import { redirect } from 'next/navigation';

export default async function Home() {
  const user = await getCurrentUser();

  if (user) {
    if (user.role === 'medical_staff') {
      redirect('/dashboard');
    } else {
      redirect('/chatbot')
    }
  } else {
    redirect('/login');
  }
}
