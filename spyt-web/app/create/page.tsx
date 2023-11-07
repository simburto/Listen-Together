"use client";
import { useState } from 'react';
import NextAuth from 'next-auth';

export default function Home() {

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 py-72">
        <div className="text-5xl font-bold">
            <h1>Create a Room</h1> 
        </div>
    </main>
  )
}
