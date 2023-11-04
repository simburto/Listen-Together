import spotipy
import spotipy.oauth2 as oauth2
from dotenv import load_dotenv
from os import getenv as env
import requests
from ytmusicapi import YTMusic

#functions needed for website TEMPORARY
#mode code guide: 0 = not using (service), 1 = hosting with (service), 2 = client with (service)
spmode = 0 
ytmode = 2 
trackname = 'Show'
artistname = 'Ado'
position_ms = 1000
ytpassword = None
ytip = 'http://localhost:9863/query'
playstate = True
leave = False

#constants
prevpos = 0
# return code guide: 0 = Nothing playing, 1 = Paused, 2 = Advertisement, 3 = Song playing
returncode = 0 #return code indicates what processes need to take place

load_dotenv()
client_id = env('API_KEY')
client_secret = env('API_SECRET')

#spd is for spotify developer access (get playlist)
client_credentials_manager = oauth2.SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spd = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

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
            return returncode, position_ms, artistname, trackname
        #if user client is open and hasn't played something yet or user client is closed
        except:
            returncode = [0]
            return returncode
    def client(trackname, artistname, position_ms, playstate, spu):# if spotify is client
        if playstate == True:
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
                spu.start_playback(uris=trackid, position_ms = position_ms)
                return trackid, artistname, trackname
            except:
                return 'An Error Occured'
        else:
            spu.pause_playback
            return 'Pause'
class youtube():
    def getEmbed(author, title,ytmusic):
        search = ytmusic.search(author + title, filter="songs")
        songID = search[0]['videoId']
        return songID
    def sendreq(json, ytpassword):
        if ytpassword:
            requests.post(url='http://localhost:9863/query', headers={f'Authorization': f'Bearer {ytpassword}'}, json=json)
        else:
            requests.post(url='http://localhost:9863/query', json=json)
    def host(ytpassword, ytip): # if youtube client is hosting
        output = []
        while len(output) == 0: 
            try: #tries to connect to local client
                if ytpassword:
                    output = requests.get(url=f'{ytip}', headers={f'Authorization': f'Bearer {ytpassword}'}).json()
                else:
                    output = requests.get(url=f'{ytip}').json()
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
            position_ms = output['player']['seekbarCurrentPosition']*1000
            returncode = 3
            return returncode, position_ms, artistname, trackname
    def client(name, artist): # if youtube client is client
        ytmusic = YTMusic()
        songID = youtube.getEmbed(artist, name, ytmusic)
        return songID
# main logic
def main(spmode: int, ytmode: int, ytpassword, ytip, spu):
    while not leave:
        try:
            if spmode == 1: # if spotify is hosting
                host = spotify.host(spu)
                return(host)
            elif ytmode == 1: # if youtube is hosting
                output = youtube.host(ytpassword, ytip)
                #check returncodes
                if output[0] == 0: 
                    return output[0]
                elif output[0] == 1:
                    return output[0]
                elif output[0] == 2:
                    return output[0]
                elif output[0] == 3:
                    trackname = output[1]
                    artistname = output[2]
                    position_ms = int(output[3])*1000
                    return(output[0], trackname, artistname, position_ms)
        except spotipy.SpotifyOauthError as e: # Refresh access token
            token = spu.refresh_access_token()
            spu = spotipy.Spotify(auth=token) 