import spotipy
import spotipy.oauth2 as oauth2
import spotipy.util as util
from dotenv import load_dotenv
from os import getenv as env

load_dotenv()
client_id = env('API_KEY')
client_secret = env('API_SECRET')
redirect_uri = 'https://callback.simburrito.repl.co/'
username = input('username')
playlist_link = input('playlist link')
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

