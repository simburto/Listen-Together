import spotipy
import spotipy.oauth2 as oauth2
from dotenv import load_dotenv
from os import getenv as env

load_dotenv()
client_id = env('test_id')
client_secret = env('test_secret')

scope = 'app-remote-control streaming user-modify-playback-state user-read-currently-playing user-read-playback-state'
print(spotipy.util.prompt_for_user_token('username',scope,client_id= client_id,client_secret = client_secret,redirect_uri='https://callback.simburrito.repl.co'))

