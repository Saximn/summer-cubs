import { getCurrentUser } from '@/lib/auth/getCurrentUser';

export default async function TestAuthPage() {
  const user = await getCurrentUser();

  return (
    <div className="p-10 text-sm">
      <h1 className="text-lg font-bold">Auth Test Page</h1>
      {user ? (
        <pre>{JSON.stringify(user, null, 2)}</pre>
      ) : (
        <p>No user is logged in.</p>
      )}
    </div>
  );
}
