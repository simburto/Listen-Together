import spotipy
import spotipy.oauth2 as oauth2
from dotenv import load_dotenv
from os import getenv as env
import requests
from ytmusicapi import YTMusic
import sqlite3
from time import sleep
import base64
import datetime

#mode code guide: 0 = not using (service), 1 = hosting with (service), 2 = client with (service)
#constants
prevpos = 0
# return code guide: 0 = Nothing playing, 1 = Paused, 2 = Advertisement, 3 = Song playing
returncode = 0 #return code indicates what processes need to take place
con = sqlite3.connect("host.db", check_same_thread=False)
cur = con.cursor()

load_dotenv()
client_id = env('SPOTIFY_ID')
client_secret = env('SPOTIFY_SECRET')
redirect_uri = env('redirect_uri')

#spd is for spotify developer access (get playlist)
client_credentials_manager = oauth2.SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spd = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

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
#spotify host and client logic
class spotify():
    def host(spu):#if spotify client is hosting
        #gets playing track
        track = spu.current_user_playing_track()
        #if user client is open and was playing something
        try:
            global prevpos
            position_ms = track['progress_ms']
            #current_user_playing_track returns the same position if the song is paused returns nothing if the client is closed
            if position_ms == prevpos:
                returncode = [1]
                return returncode
            #filters out artist name and track name to pass to clients 
            artistname = track['item']['artists'][0]['name']
            trackname = track['item']['name']
            prevpos = position_ms
            returncode = 3
            return returncode, trackname, artistname, position_ms
        #if user client is open and hasn't played something yet or user client is closed
        except:
            returncode = [0]
            return returncode    
    def client(roomcode, trackname, artistname, position_ms, playstate, refresh_token):# if spotify is client
        token_info = refreshtoken(refresh_token)
        spu = spotipy.Spotify(auth=token_info)
        if playstate == True:
            #combines artistname and trackname to get most accurate search result
            search_term = f"artist:" + artistname + " track:" + trackname
            trackid = []
            #searches spotify for type 'track' using searchterm 
            track = spd.search(q=search_term, limit=1, offset = 0, type='track', market='CA') # returns dict
            #filter dict
            trackid = [track['tracks']['items'][0]['uri']]
            artistname = track['tracks']['items'][0]['artists'][0]['name']
            trackname = track['tracks']['items'][0]['name']
            #passes uri of searched track + position of song in ms to start_playback
            spu.start_playback(uris=trackid, position_ms = int(position_ms))

            return trackid, artistname, trackname, position_ms
        else:
            spu.pause_playback
            return 'Pause'
class youtube():
    def getEmbed(author, title, ytmusic):
        search = ytmusic.search(author + title, filter="songs")
        songID = search[0]['videoId']
        return songID
    def host(roomcode, ytpassword, ytip): # if youtube client is hosting
        output = []
        while len(output) == 0: 
            try: #tries to connect to local client
                if ytpassword != 0:
                    output = requests.get(url='http://' + ytip + ':9863/query', headers={f'Authorization': f'Bearer {ytpassword}'}).json()
                else:
                    output = requests.get(url='http://' + ytip + ':9863/query').json()
            except requests.ConnectionError:
                return{
                    'isHosting': False
                }
        if output['player']['hasSong'] == False: #checks if player has a song
            returncode = [0]
            return returncode
        elif output['player']['isPaused'] == True: #checks if song within player is paused
            returncode = [1]
            return returncode
        elif output['track']['author'] == 'Video will play after ad': # check if song within player is an ad
            returncode = [2]
            return returncode
        else: #filters output to only outputs needed (tracks, artist, and progress)
            trackname = output['track']['title']
            artistname = output['track']['author']
            position_ms = output['player']['seekbarCurrentPosition']*1000
            returncode = 3
            return returncode, trackname, artistname, position_ms
    def client(name, artist): # if youtube client is client
        ytmusic = YTMusic()
        songID = youtube.getEmbed(artist, name, ytmusic)
        return songID
# main logic
def main(roomcode, spmode, ytmode, ytpassword, ytip, refresh_token):
    roomcode = int(roomcode)
    cur.execute("INSERT INTO room VALUES (?,?,?,?,?)", (roomcode, 0, None, None, 0))
    con.commit()
    while True:
        spmode = int(spmode)
        ytmode = int(ytmode)
        if spmode == 1: # if spotify is hosting
            token_info = refreshtoken(refresh_token)
            spu = spotipy.Spotify(auth=token_info)
            output = spotify.host(spu)
            if output[0] == 0: 
                cur.execute("DELETE FROM room WHERE roomcode =?", (roomcode,))
                cur.execute("INSERT INTO room VALUES (?,?,?,?,?)", (roomcode, output[0], None, None, 0))
                con.commit()
            elif output[0] == 1:
                cur.execute("DELETE FROM room WHERE roomcode =?", (roomcode,))
                cur.execute("INSERT INTO room VALUES (?,?,?,?,?)", (roomcode, output[0], None, None, 0))
                con.commit()
            elif output[0] == 2:
                cur.execute("DELETE FROM room WHERE roomcode =?", (roomcode,))
                cur.execute("INSERT INTO room VALUES (?,?,?,?,?)", (roomcode, output[0], None, None, 0))
                con.commit()
            elif output[0] == 3:
                trackname = output[1]
                artistname = output[2]
                position_ms = output[3]
                cur.execute("DELETE FROM room WHERE roomcode =?", (roomcode,))
                cur.execute("INSERT INTO room VALUES (?,?,?,?,?)", (roomcode, output[0], trackname, artistname, position_ms))
                con.commit()
        elif ytmode == 1: # if youtube is hosting
            output = youtube.host(roomcode, ytpassword, ytip)
            #check returncodes
            if output[0] == 0: 
                cur.execute("DELETE FROM room WHERE roomcode =?", (roomcode,))
                cur.execute("INSERT INTO room VALUES (?,?,?,?,?)", (roomcode, output[0], None, None, 0))
                con.commit()
            elif output[0] == 1:
                cur.execute("DELETE FROM room WHERE roomcode =?", (roomcode,))
                cur.execute("INSERT INTO room VALUES (?,?,?,?,?)", (roomcode, output[0], None, None, 0))
                con.commit()
            elif output[0] == 2:
                cur.execute("DELETE FROM room WHERE roomcode =?", (roomcode,))
                cur.execute("INSERT INTO room VALUES (?,?,?,?,?)", (roomcode, output[0], None, None, 0))
                con.commit()
            elif output[0] == 3:
                trackname = output[1]
                artistname = output[2]
                position_ms = output[3]
                cur.execute("DELETE FROM room WHERE roomcode =?", (roomcode,))
                cur.execute("INSERT INTO room VALUES (?,?,?,?,?)", (roomcode, output[0], trackname, artistname, position_ms))
                con.commit()
        sleep(1)