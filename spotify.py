#
# This file authenticates the app with spotify and provides functions to control client's spotify players
#

import flask
import base64
import requests
import spotipy
import spotipy.oauth2 as oauth2
from dotenv import load_dotenv
from os import getenv as getenv

spd = None
spotify_id = None
spotify_secret = None

def authenticate_spotify() -> None:
    global spotify_id, spotify_secret
    load_dotenv()
    spotify_id = getenv('SPOTIFY_ID')
    spotify_secret = getenv('SPOTIFY_SECRET')
    if not spotify_id or not spotify_secret:
        raise ValueError("Spotify ID or Spotify Secret not found in .env file")
        exit(1) # We want to exit here

    global spd
    client_credentials_manager = oauth2.SpotifyClientCredentials(client_id=spotify_id, client_secret=spotify_secret)
    spd = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def refreshtoken(refresh_token: str) -> str:
    global spotify_id, spotify_secret
    if not spotify_id or not spotify_secret:
        raise ValueError("Spotify ID and/or Spotify Secret are required for obtaining a refresh token")

    authorization = base64.b64encode((spotify_id + ":" + spotify_secret).encode("ascii")).decode("ascii")
    url = 'https://accounts.spotify.com/api/token'
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    headers = {
        "Authorization": "Basic " + authorization,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url=url, data=data, headers=headers).json()['access_token']
    return response
