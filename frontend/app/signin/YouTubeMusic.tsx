"use client";

import React, { useRef } from 'react';

export function InputWithButton() {
const ipInputRef = useRef<HTMLInputElement>(null);
const passInputRef = useRef<HTMLInputElement>(null);

  const handleClick = () => {
    if (ipInputRef.current && ipInputRef.current.value) {
      if (passInputRef.current && passInputRef.current.value) {
      const ytip = ipInputRef.current.value;
      const ytpass = passInputRef.current.value;
      const ytmode = 1;
      const spmode = 0; 
      const refresh_token = 0;

      fetch(`http://127.0.0.1:8080/hostroom/${spmode}/${ytmode}/${ytpass}/${ytip}/${refresh_token}`)
        .then(res => res.json())
        .then (data => {
          const roomcode = data.roomcode;
          console.log(roomcode);
          const isHosting = data.isHosting;
          console.log(isHosting);
        })
        .catch(err => {
          alert("There was an error creating your room. Please try again. Error Message: " + err.message);
        });
      } else {
        alert('Please enter a password');
      }
      
    } else {
      alert('Please enter an IP address');
    }
  };

  return (
    <div>
      {/* TODO: Make this button even if there's no password */}
      <input type="text" ref={ipInputRef} placeholder="Enter Your YTMusic IP Here"/>

      <input type="text" ref={passInputRef} placeholder="Enter Your YTMusic Password Here"/>

      <button onClick={handleClick}>Submit</button>
    
    </div>
  );
}