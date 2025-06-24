"use client";
import React, { useState, useRef, useEffect } from 'react';
import { Box, Button, TextField } from '@mui/material';

export default function ChatbotPage() {
    const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
    const [input, setInput] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const handleSendMessage = () => {
        if (!input.trim()) return;

        const userMessage = { sender: 'User', text: input };
        const botMessage = { sender: 'Bot', text: `You said: ${input}` };

        setMessages((prev) => [...prev, userMessage, botMessage]);
        setInput('');
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
                            sx={{ backgroundColor: 'white', borderRadius: '5px' }}
                        />
                        <Button
                            onClick={handleSendMessage}
                            variant="contained"
                            className="bg-background font-bold px-6 py-3"
                        >
                            Send
                        </Button>
                    </Box>
                </Box>
            </Box>
        </Box>
    );
}
