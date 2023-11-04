"use client";
import { useState } from 'react';
import { AiOutlineArrowRight } from 'react-icons/ai';

export default function Home() {

  const [isEnteringCode, setIsEnteringCode] = useState(false);
  const [code, setCode] = useState('');

  const handleButton = () => {
    setIsEnteringCode(true);
    console.log("yes")
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 py-72">
        <script src="https://www.youtube.com/iframe_api"></script>
        <div id="player"></div>
    </main>
  )
}
