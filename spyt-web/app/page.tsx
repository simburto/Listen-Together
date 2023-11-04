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
    <main className="flex min-h-screen flex-col items-center justify-between p-24 py-72 gap-5">
      <div>
        <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-teal-500 to-purple-800">
          Listen. {" "}
          <span className="text-white">
            Together.
          </span>
        </h1>
      </div>
      <div className="flex flex-col items-center gap-2">
        {
          isEnteringCode ? (
            <div className="flex flex-row items-center gap-2">
              <input
                type="text"
                className="border rounded-md px-2 py-2 bg-white text-black"
                value={code}
                placeholder="Enter join code"
                onChange={(e) => setCode(e.target.value)}
              />
              <h1 className="text-2xl">
                <AiOutlineArrowRight/>
              </h1>
            </div>
          ) : (
            <button 
              className="border rounded-md px-2 py-2 bg-white text-black font-bold"
              onClick={handleButton}>
              <div className="flex flex-row items-center">
                <h1 className="text-xl">Join a room</h1>
                <h1 className="text-xl ml-2"><AiOutlineArrowRight/></h1>
              </div>
            </button>
          )
        }
        <button className="px-2 py-2 text-white">
          Looking to host? {' '}
          <span className="underline">Create a room</span>
        </button>
      </div>
    </main>
  )
}
