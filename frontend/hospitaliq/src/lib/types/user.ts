// lib/types/user.ts
export interface User {
    id: number;
    email: string;
    fullName: string;
    role: string;
    birthday: string | null;
}
