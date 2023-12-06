from threading import Lock
import requests
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, session
import sqlite3
from dotenv import getenv as env

app = Flask(__name__)
async_mode = None
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
sqlitekey = env('SQLITE_KEY')


def background_thread():
    """Example of how to send server generated events to clients."""
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