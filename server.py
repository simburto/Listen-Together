from flask import Flask, render_template, jsonify
from flask_cors import CORS
from random import randint
from multiprocessing import Process

from ytmusicapi import YTMusic

import youtube
import spotify
import main
from os import getenv as env
import sqlite3
from threading import Lock
from flask_socketio import SocketIO, emit
from time import sleep

# return code guide: 0 = Nothing playing, 1 = Paused, 2 = Advertisement, 3 = Song playing
# mode code guide: 0 = not using (service), 1 = hosting with (service), 2 = ytclient with (service)
client_id = env('SPOTIFY_ID')
client_secret = env('SPOTIFY_SECRET')
sqlitekey = env('SQLITE_KEY')
redirect_uri = env('redirect_uri')
app = Flask(__name__)
CORS(app)
async_mode = None
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

# initialize database
con = sqlite3.connect("host.db", check_same_thread=False)
cur = con.cursor()
try:
    cur.execute("CREATE TABLE room(roomcode INT, returncode, trackname, artistname, position_ms, timeout)")
    con.commit()
except sqlite3.OperationalError:
    cur.execute("DROP TABLE room")
    cur.execute("CREATE TABLE room(roomcode INT, returncode, trackname, artistname, position_ms, timeout)")
    con.commit()
cur.close()
roomcodes = []
rooms = []


def dc(roomcode):
    con = sqlite3.connect("host.db", check_same_thread=False)
    cur = con.cursor()
    cur.execute("DELETE FROM room WHERE roomcode=?", (roomcode,))
    con.commit()
    cur.close()
    con.close()
    # Removing instance from rooms array
    if roomcode in roomcodes:
        i = roomcodes.index(roomcode)
        if i < len(rooms) and rooms[i] is not None:
            rooms[i].terminate()
            rooms[i].join()  # Wait for process termination
            del rooms[i]
            roomcodes.remove(roomcode)


@app.route('/hostroom/<spmode>/<ytmode>/<ytip>/<ytpassword>/<refresh_token>', methods=['GET'])  # ythost room
def hostroom(spmode, ytmode, ytip, ytpassword, refresh_token):
    roomcode = randint(11111111, 99999999)  # generate roomcode
    roomcodevalid = False
    while not roomcodevalid:  # check if roomcode is used or not
        if roomcode not in roomcodes:
            roomcodevalid = True
            roomcodes.append(roomcode)  # add roomcode to roomcodes list
        else:
            roomcode = randint(11111111, 99999999)
    if not roomcodevalid:
        return "Rooms full", 507
    roomcode = int(roomcode)
    if spmode == '1':
        instance = Process(target=main.main, args=(roomcode, spmode, ytmode, None, None, refresh_token))
    elif ytmode == '1':
        instance = Process(target=main.main, args=(roomcode, spmode, ytmode, ytpassword, ytip, None))
    roomcodes.append(roomcode)  # add roomcode to roomcodes list
    rooms.append(instance)  # Store the instance in the dictionary using the roomcode as the key
    instance.start()  # Start the process
    return jsonify({
        'isHosting': True,
        'roomcode': roomcode,
    })


@app.route('/spotify/<roomcode>/<refresh_token>')  # spotify enter room
def sproom(roomcode, refresh_token):
    roomcode = int(roomcode)
    if roomcode not in roomcodes:
        return "Unauthorized", 401
    while True:
        try:
            con = sqlite3.connect("host.db", check_same_thread=False)
            cur = con.cursor()
            (roomid, status, trackname, artistname, position_ms) = cur.execute("SELECT * FROM room WHERE roomcode =?",
                                                                               (roomcode,)).fetchone()
            cur.close()
            status = int(status)
            # check returncodes
            if status == 0:
                return {
                    'notUsingService': True
                }
            elif status == 1:
                spotify.client(None, None, None, None, False, refresh_token)
                return {
                    'isPaused': True
                }
            elif status == 2:
                return {
                    'isAdvertisement': True
                }
            elif status == 3:
                songid = spotify.client(roomcode, trackname, artistname, position_ms, True, refresh_token)
                return {
                    'songid': songid  # for spotify HTML embed
                }
        except TypeError:
            pass


@app.route('/youtube/<roomcode>')  # youtube get song info
def ytroom(roomcode):
    roomcode = int(roomcode)
    if roomcode not in roomcodes:
        return "Unauthorized", 401
    else:
        try:
            con = sqlite3.connect("host.db", check_same_thread=False)
            cur = con.cursor()
            (roomid, status, trackname, artistname, position_ms, timeout) = cur.execute("SELECT * FROM room WHERE roomcode =?",
                                                                               (roomcode,)).fetchone()
            cur.close()
            status = int(status)
            # Check return codes
            if status == 0:
                return {
                    'usingService': False
                }
            elif status == 1:
                return {
                    'isPaused': True,
                    'trackname': trackname,
                    'artistname': artistname
                }
            elif status == 2:
                return {
                    'isAdvertisement': True
                }
            elif status == 3:
                songid = youtube.getEmbed(artistname, trackname)
                return jsonify({
                    'isPaused': False,
                    'isAdvertisement': False,
                    'songid': songid,
                    'position_ms': position_ms,
                    'artistname': artistname,
                    'trackname': trackname
                })
        except TypeError:
            pass


@app.route('/disconnect/<roomcode>/<authkey>')
def disconnect(roomcode, authkey):
    if authkey != env('disconnect-auth-key'):
        return 'Unauthorized', 401
    roomcode = int(roomcode)
    if roomcode not in roomcodes:
        return "Room not found", 404
    return dc(roomcode)


def background_thread():
    prevdata = []
    while True:
        socketio.sleep(1)
        con = sqlite3.connect('host.db', check_same_thread=False)
        cur = con.cursor()
        data = cur.execute('SELECT * FROM room').fetchall()
        cur.close()
        if data != prevdata:
            prevdata = data
            socketio.emit('my_response',
                          {'data': data})


@app.route('/db/<sqlite_key>')
def db(sqlite_key):
    if sqlite_key != sqlitekey:
        return 'Unauthorized', 401
    else:
        return render_template('control_panel.html', async_mode=socketio.async_mode)


@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

    # When a ytclient connects, fetch and emit the initial data immediately
    con = sqlite3.connect('host.db', check_same_thread=False)
    cur = con.cursor()
    data = cur.execute('SELECT * FROM room').fetchall()
    cur.close()
    emit('initial_data', data)


def watchdog():
    while True:
        sleep(10)
        con = sqlite3.connect('host.db', check_same_thread=False)
        cur = con.cursor()
        output = cur.execute("SELECT * FROM room WHERE timeout=1").fetchall()
        cur.close()
        con.close()
        for i in range(len(output)):
            roomcode = output[i][0]
            dc(int(roomcode))


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/client/host/<roomcode>') # TODO: Fix this stupid shit
def client_host(roomcode):
    return render_template("listener_yt.html") # TODO: fix ' and " consistency


@app.route('/client/ytlistener/<roomcode>')
def client_ytlistener(roomcode):
    return render_template('player.html')


@app.route('/getVideoId/<query>', methods=['GET'])
def get_video_id(query):
    ytmusic = YTMusic()
    search = ytmusic.search(query, filter="songs")
    song_id = search[0]['videoId']
    return jsonify({'videoId': song_id})


if __name__ == '__main__':
    wd = Process(target=watchdog)
    wd.start()
    socketio.run(app, port=5000, debug=True, allow_unsafe_werkzeug=True)
