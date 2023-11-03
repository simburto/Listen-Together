from flask import Flask, request
from random import randint
from multiprocessing import Process
import main.py

app = Flask(__name__)

@app.route('')
@app.route('/createroom/<request>/<spmode>/<ytmode>/')
def createroom(request, spmode, ytmode):
    roomcode = randint(11111111,99999999)
    main()
    return {
        'request': request,
        'id': roomcode,
    }

@app.route('/hostroom/<songname>/<artistname>/<progress>/<roomcode>')
def hostroom(songname, artistname, progress, roomcode):
    
@app.route('/joinroom/<roomcode>/<spmode>/<ytmode>')
def joinroom(roomcode):
    if 
    return {
        
    }

if __name__ == '__main__':
    app.run()