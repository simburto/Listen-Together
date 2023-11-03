from flask import Flask, request, redirect, session
from random import randint
from multiprocessing import Process
import main
import spotipy
import spotipy.oauth2 as oauth2
import spotipy.util as util

# return code guide: 0 = Nothing playing, 1 = Paused, 2 = Advertisement, 3 = Song playing
# mode code guide: 0 = not using (service), 1 = hosting with (service), 2 = client with (service)

app = Flask(__name__)
sp_oauth = oauth2.SpotifyOAuth
rooms = []
roomcodes = []

@app.route('/spotifyauth') # get spotify authentication link
def spotifyauth():
    auth_url = oauth2.get_authorize_url()
    return {
        'authURL': auth_url
    }

@app.route('/spotify/callback') # WIP how to make secret??
def spcallback():
    token_info = sp_oauth.get_access_token(request.args['code'])
    session['token_info'] = token_info
    global spu
    spu = spotipy.Spotify(auth=token_info) 
    return redirect('/submit')

@app.route('/createroom/<request>') # create new room
def createroom(request):
    roomcode = randint(11111111,99999999) # generate roomcode
    roomcodevalid = False
    while not roomcodevalid: # check if roomcode is used or not
        if roomcode not in roomcodes:
            roomcodevalid = True
            return {
            'request': request,
            'id': roomcode,
            }
        else:
            roomcode = randint(11111111,99999999)
    
@app.route('/hostroom/<roomcode>/<spmode>/<ytmode>/<ytpassword>/<ytip>') # host room
def hostroom(roomcode, spmode, ytmode, ytpassword, ytip):
    if spmode == 1: # if using spotify
        exec = roomcode, Process(target=main.main(), args=(spmode, ytmode, None, None, spu))
    elif ytmode == 1: # if using youtubemusic
        exec = roomcode, Process(target=main.main(), args=(spmode, ytmode, ytpassword, ytip, None))
    exec[1].start() # starts new instance of main.py
    rooms[len(rooms)+1] = exec # adds instance to array of instances to be accessed by client
    return {
        'isHosting': True
    }

@app.route('/joinroom/<roomcode>/<spmode>/<ytmode>') # join room
def joinroom(roomcode, spmode, ytmode):
    if roomcode in roomcodes: # check if roomcode exists
        for i in range(len(rooms)): # find roomPos and roomcode (prevent brute force attack)
            if rooms[i][0] == roomcode and spmode == 2:
                return {
                    'roomPos': i,
                    'roomCode': roomcode,
                    'method': 'SpClient'
                }
            elif rooms[i][0] == roomcode and ytmode ==2:
                return {
                    'roomPos': i,
                    'roomCode': roomcode,
                    'method': 'YTClient'
                }
    else:
        return{
            'error': 404,
            'desc': 'RoomNotFound'
        }
    
@app.route('/room/spotify/<i>/<roomcode>') # spotify enter room
def sproom(i, roomcode):
    if roomcode != rooms[i][0]: # prevent brute force attack
        return{
            'error': 401,
            'desc': 'Unauthorized'
        }
    host = rooms[i][1].join() # join session
    #check returncodes
    if host[0] == 0: 
        return {
            'notUsingService': True
        }
    elif host[0] == 1:
        return {
            'isPaused': True
        }
    elif host[0] == 2:
        return {
            'isAdvertisement': True
        }
    elif host[0] == 3:
        position_ms = host[1]
        artistname = host[2]
        trackname = host[3]
        songid = main.spotify.client(trackname, artistname, position_ms, spu)[0]
        return {
            'songid': songid # for spotify HTML embed
        }

@app.route('/room/youtube/<i>') # youtube enter room
def ytroom(i, roomcode):
    if roomcode != rooms[i][0]: # prevent brute force attack
        return{
            'error': 401,
            'desc': 'Unauthorized'
        }
    host = rooms[i][1].join() # join room
    #check returncodes
    if host[0] == 0: 
        return {
            'notUsingService': True
        }
    elif host[0] == 1:
        return {
            'isPaused': True
        }
    elif host[0] == 2:
        return {
            'isAdvertisement': True
        }
    elif host[0] == 3:
        position_ms = host[1]
        artistname = host[2]
        trackname = host[3]
        songid = main.youtube.client(trackname, artistname, position_ms)[0] # MAIN.YOUTUBE.CLIENT IS NOT DONE YET!!
        return {
            'songid': songid
        }

@app.route('/disconnect')
#find how to figure out when host is disconnected, if spotify clear host cache, free roomPos and roomcode

if __name__ == '__main__':
    app.run()