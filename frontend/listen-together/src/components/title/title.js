import React, { useState } from 'react';
import styles from './title.module.css';

const Title = () => {
  const hostClick = () => {
    alert("unfinished lmao"); // TODO: make the host button work
  };

  const [selectedButton, setSelectedButton] = useState(null);
  const handleToggleButtons = (button) => {
    setSelectedButton(button);
  };

  return (
    <div className={styles.title}>
      <header>
        <h1>Listen to Youtube Music and Spotify With Your Friends!</h1>
      </header>

      <p>First, select your platform. Then enter your room code if you're joining, or click host if you're hosting.</p>

      {/* 2nd div for choosing what platform they're using */}
      <div className={styles.toggleButtons}>
        <button
          onClick={() => handleToggleButtons('spotify')}
          className={selectedButton === 'spotify' ? styles.selectedSpotify : ''}
        >
          Spotify
        </button>

        <button
          onClick={() => handleToggleButtons('youtube music')}
          className={selectedButton === 'youtube music' ? styles.selectedYoutubeMusic : ''}
        >
          Youtube Music 
        </button>
      </div>
      <input type="text" placeholder="Enter your room code" />

      <button onClick={hostClick}>
        Looking to Host?
      </button>

      
    </div>
  );
};

export default Title;
