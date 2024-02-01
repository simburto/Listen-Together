"use client";
import React, { useEffect } from 'react';
import YoutubePlayer from 'youtube-player';
const room

function createPlayer() {
  const player = YoutubePlayer('video-player', {
    // Params: https://developers.google.com/youtube/player_parameters#Parameters
    height: '200',
    width: '200',
    videoId: 'QeEzZW3TkOc',
  });
}

function getVideo() {
  fetch (`http://127.0.0.1:8080/youtube/getVideo/${roomcode}`)
}

function YTPlayer() {

  useEffect(() => {

  });
  

  return <div id='video-player'></div>
}

export default YTPlayer 