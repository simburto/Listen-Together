"use ytclient";

import React, { useEffect } from 'react';
import YoutubePlayer from 'youtube-player';

let player;
function createPlayer() {
  player = YoutubePlayer('video-player', {
    height: '200',
    width: '200',
    videoId: 'QeEzZW3TkOc',
  });

  // Additional event handling (optional)
  player.on('ready', (event) => {
    // Do something when the player is ready
    console.log('Player is ready');
  });
}
function pauseVideo() {
  if (player && player.pauseVideo) {
    player.pauseVideo();
  }
}

function playVideo() {
  if (player && player.playVideo) {
    player.playVideo();
  }
}

function changeVideo(videoId) {
  if (player && player.loadVideoById) {
    player.loadVideoById(videoId);
  }
}

function periodic() {
  const interval = setInterval(() => {
    console.log("prints every 5 seconds");
  }, 5000); // 5000ms = 5 seconds

  return () => clearInterval(interval);
}

function YTPlayer() {
  useEffect(() => {
    createPlayer();
    periodic()
  }, []);

  return <div id='video-player'></div>;
}

export default YTPlayer;
