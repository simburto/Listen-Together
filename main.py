import spotipy
import spotipy.oauth2 as oauth2
from dotenv import load_dotenv
from os import getenv as env
import requests
import sqlite3
from time import sleep
import base64
from datetime import datetime

import spotify
import youtube

# mode code guide: 0 = not using (service), 1 = hosting with (service), 2 = ytclient with (service)
# constants
prevpos = 0
prevtime = None
# return code guide: 0 = Nothing playing, 1 = Paused, 2 = Advertisement, 3 = Song playing
returncode = 0  # return code indicates what processes need to take place

load_dotenv()
client_id = env('SPOTIFY_ID')
client_secret = env('SPOTIFY_SECRET')
redirect_uri = env('redirect_uri')

# spd is for spotify developer access (get playlist)
client_credentials_manager = oauth2.SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spd = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def refreshtoken(refresh_token):
    global freshtoken
    authorization = base64.b64encode((client_id + ":" + client_secret).encode("ascii")).decode("ascii")
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


def checkAFK(prevtime, roomcode, output):
    con = sqlite3.connect("host.db", check_same_thread=False)
    cur = con.cursor()
    if prevtime == None:
        cur.execute("DELETE FROM room WHERE roomcode =?", (roomcode,))
        cur.execute("INSERT INTO room VALUES (?,?,?,?,?,?)", (roomcode, output[0], prevTrack, prevArtist, 0, 0))
        con.commit()
        cur.close()
        con.close()
        prevtime = datetime.now()
        return prevtime
    timedelta = (datetime.now() - prevtime).seconds
    if timedelta > 300:
        cur.execute("DELETE FROM room WHERE roomcode =?", (roomcode,))
        cur.execute("INSERT INTO room VALUES (?,?,?,?,?,?)", (roomcode, output[0], prevTrack, prevArtist, 0, 1))
        con.commit()
        cur.close()
        con.close()
        return 3
    else:
        return prevtime


# main logic
def main(roomcode, spmode, ytmode, ytpassword, ytip, refresh_token):
    global prevtime, prevTrack, prevArtist
    prevTrack, prevArtist = None, None
    con = sqlite3.connect("host.db", check_same_thread=False)
    cur = con.cursor()
    roomcode = int(roomcode)
    cur.execute("INSERT INTO room VALUES (?,?,?,?,?,?)", (roomcode, 0, prevTrack, prevArtist, 0, datetime.now()))
    con.commit()
    cur.close()
    con.close()
    while True:
        con = sqlite3.connect("host.db", check_same_thread=False)
        cur = con.cursor()
        spmode = int(spmode)
        ytmode = int(ytmode)
        if spmode == 1:  # if spotify is hosting
            token_info = refreshtoken(refresh_token)
            spu = spotipy.Spotify(auth=token_info)
            output = spotify.host(spu)
            if output[0] == 0:
                prevtime = checkAFK(prevtime, roomcode, output)
                if prevtime == 3:
                    return "deez nuts"
            elif output[0] == 1:
                prevtime = checkAFK(prevtime, roomcode, output)
                if prevtime == 3:
                    return "deez nuts"
            elif output[0] == 2:
                cur.execute("DELETE FROM room WHERE roomcode =?", (roomcode,))
                cur.execute("INSERT INTO room VALUES (?,?,?,?,?,?)", (roomcode, output[0], prevTrack, prevArtist, 0, None))
                con.commit()
            elif output[0] == 3:
                trackname = output[1]
                prevTrack = trackname
                artistname = output[2]
                prevArtist = artistname
                position_ms = output[3]
                cur.execute("DELETE FROM room WHERE roomcode =?", (roomcode,))
                cur.execute("INSERT INTO room VALUES (?,?,?,?,?,?)",
                            (roomcode, output[0], trackname, artistname, position_ms, None))
                con.commit()
        elif ytmode == 1:  # if youtube is hosting
            output = youtube.host(roomcode, ytpassword, ytip)
            #check returncodes
            if output[0] == 0:
                prevtime = checkAFK(prevtime, roomcode, output)
                if prevtime == 3:
                    return "deez nuts"
            elif output[0] == 1:
                prevtime = checkAFK(prevtime, roomcode, output)
                if prevtime == 3:
                    return "deez nuts"
            elif output[0] == 2:
                prevtime = None
                cur.execute("DELETE FROM room WHERE roomcode =?", (roomcode,))
                cur.execute("INSERT INTO room VALUES (?,?,?,?,?,?)", (roomcode, output[0], prevTrack, prevArtist, 0, None))
                con.commit()
            elif output[0] == 3:
                prevtime = None
                trackname = output[1]
                prevTrack = trackname
                artistname = output[2]
                prevArtist = artistname
                position_ms = output[3]
                cur.execute("DELETE FROM room WHERE roomcode =?", (roomcode,))
                cur.execute("INSERT INTO room VALUES (?,?,?,?,?,?)",
                            (roomcode, output[0], trackname, artistname, position_ms, None))
                con.commit()
        sleep(1)
        cur.close()
        con.close()
