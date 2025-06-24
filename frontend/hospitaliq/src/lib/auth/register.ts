export async function registerToDjango(
  email: string,
  password: string,
  fullname: string,
  birthday: string // e.g. 'YYYY-MM-DD'
) {
  const res = await fetch(`${process.env.BACKEND_URL}/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, fullname, birthday }),
  });

  if (!res.ok) {
    throw res;
  }

  return await res.json();
}
