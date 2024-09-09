import spotipy
from dotenv import load_dotenv
from os import getenv as env

from spotipy import oauth2

from main import refreshtoken

load_dotenv()
client_id = env('SPOTIFY_ID')
client_secret = env('SPOTIFY_SECRET')
#spd is for spotify developer access (get playlist)
client_credentials_manager = oauth2.SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spd = spotipy.Spotify(client_credentials_manager = client_credentials_manager)


def host(spu):#if spotify ytclient is hosting
    #gets playing track
    track = spu.current_user_playing_track()
    #if user ytclient is open and was playing something
    try:
        global prevpos
        position_ms = track['progress_ms']
        #current_user_playing_track returns the same position if the song is paused returns nothing if the ytclient is closed
        if position_ms == prevpos:
            returncode = [1]
            return returncode
        #filters out artist name and track name to pass to clients
        artistname = track['item']['artists'][0]['name']
        trackname = track['item']['name']
        prevpos = position_ms
        returncode = 3
        return returncode, trackname, artistname, position_ms
    #if user ytclient is open and hasn't played something yet or user ytclient is closed
    except:
        returncode = [0]
        return returncode
def client(roomcode, trackname, artistname, position_ms, playstate, refresh_token):# if spotify is ytclient
    # TODO: 'roomcode' is never used here
    token_info = refreshtoken(refresh_token)
    spu = spotipy.Spotify(auth=token_info)
    if playstate == True:
        #combines artistname and trackname to get most accurate search result
        search_term = f"artist:" + artistname + " track:" + trackname
        trackid = []
        #searches spotify for type 'track' using searchterm
        track = spd.search(q=search_term, limit=1, offset=0, type='track', market='CA') # returns dict
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
