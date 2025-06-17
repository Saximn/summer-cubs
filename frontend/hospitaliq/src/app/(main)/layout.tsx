import React from 'react';
import Navbar from "./_components/Navbar";

export default function MainLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <main className="flex flex-col min-h-screen">
            <Navbar />
            {children}
        </main>
    )
}