import spotipy
import spotipy.oauth2 as oauth2
import spotipy.util as util
from dotenv import load_dotenv
from os import getenv as env
from time import sleep
import requests

#functions needed for website
#mode code guide: 0 = not using (service), 1 = hosting with (service), 2 = client with (service)
spmode = 0 
ytmode = 1 
trackname = 'Show'
artistname = 'Ado'
offset = 1000

#constants
prevpos = 0
#return code indicates what processes need to take place
returncode = 0

load_dotenv()
client_id = env('API_KEY')
client_secret = env('API_SECRET')
redirect_uri = 'https://callback.simburrito.repl.co/'

#spd is for spotify developer access (get playlist)
client_credentials_manager = oauth2.SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spd = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

#spotify host and client logic
class spotify():
    def host():#if spotify client is hosting
        #gets playing track
        track = spu.current_user_playing_track()
        #if user client is open and was playing something
        try:
            global prevpos
            position_ms = track['progress_ms']
            #current_user_playing_track returns the same position if the song is paused returns nothing if the client is closed
            if position_ms == prevpos:
                returncode = [0]
                return returncode
            #filters out artist name and track name to pass to clients 
            artistname = track['item']['artists'][0]['name']
            trackname = track['item']['name']
            prevpos = position_ms
            returncode = 1
            return returncode, position_ms, artistname, trackname
        #if user client is open and hasn't played something yet or user client is closed
        except:
            returncode = [2]
            return returncode
    def client(trackname, artistname, offset):# if spotify is client
        try:
            #combines artistname and trackname to get most accurate search result
            search_term = f"{artistname}%20{trackname}" 
            trackid = []
            #searches spotify for type 'track' using searchterm 
            track = spd.search(q=search_term, limit=1, offset = 0, type='track', market='CA') # returns dict

            #filter dict
            trackid = [track['tracks']['items'][0]['uri']]
            artistname = track['tracks']['items'][0]['artists'][0]['name']
            trackname = track['tracks']['items'][0]['name']

            #passes uri of searched track + position of song in ms to start_playback
            spu.start_playback(uris=trackid, position_ms = offset)
            return trackid, artistname, trackname
        except:
            return 'An Error Occured'
class youtube():
    def host(): # if youtube client is hosting
        output = []
        while len(output) == 0: 
            try: #tries to connect to local client
                output = requests.get(url='http://localhost:9863/query').json()
            except requests.ConnectionError:
                print("Connection Error. Is the client open?. Is remote control enabled in integration panel?.")
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
            position_ms = output['player']['seekbarCurrentPosition']
            returncode = 3
            return returncode, trackname, artistname, position_ms
    def client(): # if youtube client is client
        print("not done yet")
        #//TODO
# main logic
while True:
    if spmode != 0: # authenticate spotify user
        #spu is for spotify user specific access (get user, get user-playlist)
        username = input('username')
        scopes = 'app-remote-control streaming user-modify-playback-state user-read-currently-playing user-read-playback-state'
        token = util.prompt_for_user_token(username, scopes, client_id, client_secret, redirect_uri)
        spu = spotipy.Spotify(auth=token)
    if spmode == 1: # if spotify is hosting
        host = spotify.host()
         #check returncodes
        if host[0] == 0: 
            print('Paused')
        elif host[0] == 1:
            position_ms = host[1]
            artistname = host[2]
            trackname = host[3]
            print(trackname, artistname, position_ms)
            #broadcast these //TODO
        elif host[0] == 2:
            print("Nothing is playing")
    elif spmode == 2: # if spotify is client
        print(spotify.client(trackname, artistname, offset))
        #request these //TODO
    elif ytmode == 1: # if youtube is hosting
        output = youtube.host()
         #check returncodes
        if output[0] == 0: 
            print('Nothing is playing')
        elif output[0] == 1:
            print("Paused")
        elif output[0] == 2:
            print("Advertisement")
        elif output[0] == 3:
            trackname = output[1]
            artistname = output[2]
            position_ms = int(output[3])*1000
            print(trackname, artistname, position_ms)
            #broadcast these //TODO
    elif ytmode == 2: # if youtube is client
        print(youtube.client(trackname, artistname, position_ms))
        # request these //TODO