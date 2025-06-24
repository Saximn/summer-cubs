import { getCurrentUser } from "@/lib/auth/getCurrentUser";
import { redirect } from "next/navigation";

export default async function ProtectedLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    const user = await getCurrentUser();

    // if (!user) {
    //     redirect("/login");
    // }

    return (
        <>
            {children}
        </>
    );
}