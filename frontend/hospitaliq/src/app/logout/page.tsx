
import { logoutAction } from "./actions";
import { redirect } from 'next/navigation';

export default async function LogoutPage() {
  await logoutAction();
  redirect('/login');
}