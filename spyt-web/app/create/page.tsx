"use client";
import { useSession, signIn, signOut, SessionProvider } from "next-auth/react"

export default function Home() {
  const { data: session } = useSession();
  return (
    <SessionProvider>
      <main className="flex min-h-screen flex-col items-center justify-between p-24 py-72">
        <div className="text-5xl font-bold">
            <h1>Create a Room</h1>
            <button onClick={() => signIn()}>
              Click me
            </button> 
        </div>
      </main>
    </SessionProvider>
    
  )
}
