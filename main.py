import spotipy
import spotipy.oauth2 as oauth2
import spotipy.util as util
from dotenv import load_dotenv
from os import getenv as env
from time import sleep

#functions needed for website
sphost = 1 #sphost code guide: 0 = not using spotify, 1 = hosting with spotify, 2 = client with spotify
trackname = 'Show'
artistname = 'Ado'
offset = 1000

#constants
prevpos = 0

load_dotenv()
client_id = env('API_KEY')
client_secret = env('API_SECRET')
redirect_uri = 'https://callback.simburrito.repl.co/'
username = input('username')
if len(client_id) != 0 and len(client_secret) != 0:
    print(".env values imported")
else:
    print(".env values failed to import")
    exit()
sleep(0.01)
#spd is for spotify developer access (get playlist)
client_credentials_manager = oauth2.SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spd = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

#spu is for spotify user specific access (get user, get user-playlist)
scopes = 'app-remote-control streaming user-modify-playback-state user-read-currently-playing user-read-playback-state'
token = util.prompt_for_user_token(username, scopes, client_id, client_secret, redirect_uri)
spu = spotipy.Spotify(auth=token)

#spotify host and client logic
class spotify():
    #return code indicates what processes need to take place
    returncode = 0
    #if spotify client is hosting
    def host():
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
    # if spotify is client
    def client(trackname, artistname, offset):
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
# main logic
while True:
    if sphost == 1: # if spotify is hosting
        host = spotify.host()

         #check returncodes
        if host[0] == 0: 
            print('Paused')
        elif host[0] == 1:
            position_ms = host[1]
            artistname = host[2]
            trackname = host[3]
            print(host)
        elif host[0] == 2:
            print("Nothing is playing")
    elif sphost == 2:
        print(spotify.client(trackname, artistname, offset))