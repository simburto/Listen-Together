from flask import Flask, redirect, session, render_template
from random import randint
from multiprocessing import Process
import main
import spotipy
from os import getenv as env
import sqlite3
from threading import Lock
from flask_socketio import SocketIO, emit

# return code guide: 0 = Nothing playing, 1 = Paused, 2 = Advertisement, 3 = Song playing
# mode code guide: 0 = not using (service), 1 = hosting with (service), 2 = client with (service)
client_id = env('SPOTIFY_ID')
client_secret = env('SPOTIFY_SECRET')
sqlitekey = env('SQLITE_KEY')
redirect_uri = env('redirect_uri')
app = Flask(__name__)
async_mode = None
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

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

def disconnect(roomcode):
    try:
        con = sqlite3.connect("host.db", check_same_thread=False)
        cur = con.cursor()
        cur.execute("DELETE FROM room WHERE roomcode =?", (roomcode,))
        con.commit()
        con.close()

        if roomcode in roomcodes:
            i = roomcodes.index(roomcode)
            if i < len(rooms) and rooms[i] is not None:
                rooms[i].terminate()
                rooms[i].join()  # Wait for process termination
                del rooms[i]
                roomcodes.remove(roomcode)

        return {
            'disconnected': True
        }
    except Exception as e:
        return f"Error: {str(e)}", 500
    finally:
        # Refresh the database data here
        con = sqlite3.connect("host.db", check_same_thread=False)
        cur = con.cursor()
        data = cur.execute("SELECT * FROM room").fetchall()
        con.close()
        # Update rooms and roomcodes list based on refreshed data
        rooms.clear()
        roomcodes.clear()
        for row in data:
            roomcodes.append(row[0])  # Assuming roomcode is in the first position of the row

@app.route('/') # initial route
def index():
    return redirect('https://shockingbravecores.simburrito.repl.co/')

@app.route('/hostroom/<spmode>/<ytmode>/<ytpassword>/<ytip>/<refresh_token>')  # host room
def hostroom(spmode, ytmode, ytpassword, ytip, refresh_token):
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
        instance = Process(target=main.main, args=(roomcode, spmode, ytmode, None, None, refresh_token))
    elif ytmode == '1': 
        instance = Process(target=main.main, args=(roomcode, spmode, ytmode, ytpassword, ytip, None))
    roomcodes.append(roomcode) # add roomcode to roomcodes list
    rooms.append(instance)# Store the instance in the dictionary using the roomcode as the key
    instance.start()  # Start the process
    return {
        'isHosting': True,
        'roomcode': roomcode,
    }

@app.route('/spotify/<roomcode>/<refresh_token>') # spotify enter room
def sproom(roomcode, refresh_token):
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
                main.spotify.client(None, None, None, None, False, refresh_token)
                return {
                    'isPaused': True
                }
            elif status == 2:
                return {
                    'isAdvertisement': True
                }
            elif status == 3:
                songid = main.spotify.client(roomcode, trackname, artistname, position_ms, True, refresh_token)
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
                return {
                    'isPaused': False,
                    'songid': songid,
                    'position_ms': position_ms,
                }
        except TypeError:
            pass

@app.route('/disconnect/<roomcode>/<authkey>')
def disconnect(roomcode, authkey):
    if authkey != env('disconnect-auth-key'):
        return 'Unauthorized', 401
    roomcode = int(roomcode)
    if roomcode not in roomcodes:
        return "Room not found", 404
    return(disconnect(roomcode))

def background_thread():
    data = []
    prevdata = []
    while True:
        socketio.sleep(1)
        con = sqlite3.connect('host.db', check_same_thread=False)
        cur = con.cursor()
        data = cur.execute('SELECT * FROM room').fetchall()
        con.close()
        if data != prevdata:
            prevdata = data
            socketio.emit('my_response',
                        {'data': data})

@app.route('/db/<sqlite_key>')
def db(sqlite_key):
    if sqlite_key != sqlitekey:
        return 'Unauthorized', 401
    else:
        return render_template('index.html', async_mode=socketio.async_mode)

@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

    # When a client connects, fetch and emit the initial data immediately
    con = sqlite3.connect('host.db', check_same_thread=False)
    cur = con.cursor()
    data = cur.execute('SELECT * FROM room').fetchall()
    con.close()
    emit('initial_data', data)

#def watchdog():
 #   while True:

if __name__ == '__main__':
    socketio.run(app)