from flask import Flask, redirect
from random import randint
from multiprocessing import Process
import main
import spotipy
from os import getenv as env
import sqlite3

# return code guide: 0 = Nothing playing, 1 = Paused, 2 = Advertisement, 3 = Song playing
# mode code guide: 0 = not using (service), 1 = hosting with (service), 2 = client with (service)
client_id = env('SPOTIFY_ID')
client_secret = env('SPOTIFY_SECRET')
sqlitekey = env('SQLITE_KEY')
app = Flask(__name__)

#initialize database
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
roomcodes = []
rooms = []

@app.route('/') # initial route
def index():
    return redirect('https://shockingbravecores.simburrito.repl.co/')

@app.route('/hostroom/<spmode>/<ytmode>/<ytpassword>/<ytip>/<token_info>')  # host room
def hostroom(spmode, ytmode, ytpassword, ytip, token_info, ):
    roomcode = randint(11111111,99999999) # generate roomcode
    roomcodevalid = False
    while not roomcodevalid: # check if roomcode is used or not
        if roomcode not in roomcodes:
            roomcodevalid = True
            roomcodes.append(roomcode) # add roomcode to roomcodes list
        else:
            roomcode = randint(11111111,99999999)
    if not roomcodevalid:
        return "Rooms full", 507
    roomcode = int(roomcode)
    if spmode == '1': 
        instance = Process(target=main.main, args=(roomcode, spmode, ytmode, None, None, token_info))
    elif ytmode == '1': 
        instance = Process(target=main.main, args=(roomcode, spmode, ytmode, ytpassword, ytip, None))
    roomcodes.append(roomcode) # add roomcode to roomcodes list
    rooms.append(instance)# Store the instance in the dictionary using the roomcode as the key
    instance.start()  # Start the process
    return {
        'isHosting': True,
        'roomcode': roomcode,
    }

@app.route('/spotify/<roomcode>/<token_info>') # spotify enter room
def sproom(roomcode, token_info):
    roomcode = int(roomcode)
    if roomcode not in roomcodes:
        return "Unauthorized", 401 
    while True:
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
                main.spotify.client(None, None, None, None, False, spu)
                return {
                    'isPaused': True
                }
            elif status == 2:
                return {
                    'isAdvertisement': True
                }
            elif status == 3:
                spu = spotipy.Spotify(auth=token_info)
                songid = main.spotify.client(roomcode, trackname, artistname, position_ms, True, spu)
                return {
                    'songid': songid # for spotify HTML embed
                }
        except TypeError:
            pass

@app.route('/youtube/<roomcode>') # youtube enter room
def ytroom(roomcode):
    roomcode = int(roomcode)
    if roomcode not in roomcodes:
        return "Unauthorized", 401 
    while True:
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
                print('here x3')
                return {
                    'isPaused': False,
                    'songid': songid,
                    'position_ms': position_ms,
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
    while roomcode != roomcodes[i]:
        i=i+1
    rooms[i].terminate()
    rooms[i] = None
    roomcodes.remove(roomcode)
    return {
        'disconnected': True
    }

@app.route('/db/<sqlite_key>')
def db(sqlite_key):
    if sqlite_key != sqlitekey:
        return "Unauthorized", 401
    else:
        con = sqlite3.connect("host.db", check_same_thread=False)
        cur = con.cursor()
        return cur.execute("SELECT * FROM room").fetchall()
if __name__ == '__main__':
        app.run()