from flask import Flask
from random import randint
from multiprocessing import Process, Queue
import main
import spotipy
from os import getenv as env
import sqlite3
from time import sleep

# return code guide: 0 = Nothing playing, 1 = Paused, 2 = Advertisement, 3 = Song playing
# mode code guide: 0 = not using (service), 1 = hosting with (service), 2 = client with (service)
client_id = env('API_KEY')
client_secret = env('API_SECRET')
app = Flask(__name__)

#initialize database
rooms = []
con = sqlite3.connect("host.db", check_same_thread=False)
cur = con.cursor()
try:
    cur.execute("CREATE TABLE room(roomcode INT, returncode, trackname, artistname, position_ms)")
    con.commit()
except sqlite3.OperationalError:
    cur.execute("DROP TABLE room")
    cur.execute("CREATE TABLE room(roomcode INT, returncode, trackname, artistname, position_ms)")
    con.commit()
con.close()
for i in range(11111111,111111111):
    rooms.append(None)
roomcodes = []

@app.route('/getroomcode') # create new room
def getroomcode():
    roomcode = randint(11111111,99999999) # generate roomcode
    roomcodevalid = False
    while not roomcodevalid: # check if roomcode is used or not
        if roomcode not in roomcodes:
            roomcodevalid = True
            roomcodes.append(roomcode) # add roomcode to roomcodes list
            return {
            'id': roomcode,
            }
        else:
            roomcode = randint(11111111,99999999)
    return "Rooms full", 507
    
@app.route('/hostroom/<roomcode>/<spmode>/<ytmode>/<ytpassword>/<ytip>/<token_info>')  # host room
def hostroom(roomcode, spmode, ytmode, ytpassword, ytip, token_info):
    roomcode = int(roomcode)
    if roomcode not in roomcodes:
        return "Unauthorized", 401 
    if spmode == '1': 
        instance = Process(target=main.main, args=(roomcode, spmode, ytmode, None, None, token_info))
    elif ytmode == '1': 
        instance = Process(target=main.main, args=(roomcode, spmode, ytmode, ytpassword, ytip, None))
    roomcodes.append(roomcode) # add roomcode to roomcodes list
    rooms[roomcode] = instance  # Store the instance in the dictionary using the roomcode as the key
    instance.start()  # Start the process
    return {
        'isHosting': True
    }
    
@app.route('/room/spotify/<roomcode>/<token_info>') # spotify enter room
def sproom(roomcode, token_info):
    roomcode = int(roomcode)
    if roomcode not in roomcodes:
        return "Unauthorized", 401 
    host = None
    while host == None:
        try:
            con = sqlite3.connect("host.db", check_same_thread=False)
            cur = con.cursor()
            (roomid, status, trackname, artistname, position_ms) = cur.execute("SELECT * FROM room WHERE roomcode =?", (roomcode,)).fetchone()
            con.close()
            status = int(status)
            #check returncodes
            if status == 0: 
                return {
                    'notUsingService': True
                }
            elif status == 1:
                spu = spotipy.Spotify(auth=token_info)
                main.spotify.client(None, None, None, True, spu)
                return {
                    'isPaused': True
                }
            elif status == 2:
                return {
                    'isAdvertisement': True
                }
            elif status == 3:
                spu = spotipy.Spotify(auth=token_info)
                songid = main.spotify.client(trackname, artistname, position_ms, True, spu)[0]
                return {
                    'songid': songid # for spotify HTML embed
                }
        except TypeError:
            pass
@app.route('/room/youtube/<roomcode>') # youtube enter room
def ytroom(roomcode):
    roomcode = int(roomcode)
    if roomcode not in roomcodes:
        return "Unauthorized", 401 
    host = None
    while host is None:
        try:
            con = sqlite3.connect("host.db", check_same_thread=False)
            cur = con.cursor()
            (roomid, status, trackname, artistname, position_ms) = cur.execute("SELECT * FROM room WHERE roomcode =?", (roomcode,)).fetchone()
            con.close()
            status = int(status)
            # Check return codes
            if status == 0:
                return {
                    'notUsingService': True
                }
            elif status == 1:
                return {
                    'isPaused': True
                }
            elif status == 2:
                return {
                    'isAdvertisement': True
                }
            elif status == 3:
                songid = main.youtube.client(trackname, artistname)
                return {
                    'isPaused': False,
                    'songid': songid,
                    'position_ms': position_ms
                }
        except TypeError:
            pass

@app.route('/disconnect/<roomcode>')
#find how to figure out when host is disconnected, if spotify clear host cache, free roomPos and roomcode
def disconnect(roomcode):
    con = sqlite3.connect("host.db", check_same_thread=False)
    cur = con.cursor()
    cur.execute("DELETE FROM room WHERE roomcode =?", (roomcode,))
    con.commit()
    con.close()
    rooms[roomcode].terminate()
    rooms[roomcode] = None
    roomcodes.remove(roomcode)
    return {
        'disconnected': True
    }

if __name__ == '__main__':
    app.run()