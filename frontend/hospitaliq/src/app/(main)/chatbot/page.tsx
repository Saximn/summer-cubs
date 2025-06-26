"use client";
import React, { useState, useRef, useEffect } from 'react';
import { Box, Button, TextField } from '@mui/material';

export default function ChatbotPage() {
    const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const handleSendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = { sender: 'User', text: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/chatbot/chatbot/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: input }),
            });

            if (!res.ok) {
                throw new Error(`API error: ${res.status}`);
            }

            const data = await res.json();
            const botMessage = { sender: 'Bot', text: data.reply };
            setMessages((prev) => [...prev, botMessage]);
        } catch (error: any) {
            setMessages((prev) => [
                ...prev,
                { sender: 'Bot', text: '⚠️ Error contacting chatbot. Please try again.' },
            ]);
            console.error('Chatbot error:', error);
        } finally {
            setLoading(false);
        }
    };

    // Scroll to bottom on new message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <Box className="w-full h-full px-4 py-6 flex justify-center items-center">
            <Box className="flex flex-col gap-6 w-full max-w-[1075px]">

                {/* Chat Display */}
                <Box className="bg-primary rounded p-6 shadow-md w-full h-[400px] overflow-y-auto text-white flex flex-col gap-3">
                    <h4 className="font-bold text-3xl mb-2">Chatbot</h4>
                    {messages.map((message, index) => (
                        <Box
                            key={index}
                            className={`flex ${message.sender === 'User' ? 'justify-end' : 'justify-start'}`}
                        >
                            <Box
                                className={`px-4 py-2 rounded-lg max-w-[70%] break-words ${
                                    message.sender === 'User'
                                        ? 'bg-blue-500 text-white'
                                        : 'bg-gray-300 text-black'
                                }`}
                            >
                                {message.text}
                            </Box>
                        </Box>
                    ))}
                    <div ref={messagesEndRef} />
                </Box>

                {/* Input Section */}
                <Box className="bg-primary rounded p-6 shadow-md w-full">
                    <h4 className="font-bold text-2xl text-white mb-4">Send a Message</h4>
                    <Box className="flex flex-col md:flex-row gap-4">
                        <TextField
                            fullWidth
                            variant="outlined"
                            placeholder="Type your message..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') handleSendMessage();
                            }}
                            sx={{ backgroundColor: 'white', borderRadius: '5px' }}
                            disabled={loading}
                        />
                        <Button
                            onClick={handleSendMessage}
                            variant="contained"
                            className="bg-background font-bold px-6 py-3"
                            disabled={loading}
                        >
                            {loading ? 'Sending...' : 'Send'}
                        </Button>
                    </Box>
                </Box>
            </Box>
        </Box>
    );
}
