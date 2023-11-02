import spotipy
import spotipy.oauth2 as oauth2
import spotipy.util as util
from dotenv import load_dotenv
from os import getenv as env

#functions needed for website
sphost = False
trackname = 'Show'
artistname = 'Ado'
offset = 100

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

#spd is for developer access (get playlist)
client_credentials_manager = oauth2.SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spd = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

#spu is for user specific access (get user, get user-playlist)
scopes = 'app-remote-control streaming user-modify-playback-state user-read-currently-playing user-read-playback-state'
token = util.prompt_for_user_token(username, scopes, client_id, client_secret, redirect_uri)
spu = spotipy.Spotify(auth=token)

def spotify(sphost, trackname, artistname, offset):
    if sphost == True:
        track = spu.current_user_playing_track()
        return track
    else:
        search_term = f"{artistname}%20{trackname}" 
        trackid = []
        track = spd.search(q=search_term, limit=1, offset = 0, type='track', market='CA')
        print(type(track))
        trackid = [track['tracks']['items'][0]['uri']]
        artistname = track['tracks']['items'][0]['artists'][0]['name']
        trackname = track['tracks']['items'][0]['name']
        spu.start_playback(uris=trackid, position_ms = offset)
        return trackid, artistname, trackname
print(spotify(sphost, trackname, artistname, offset))