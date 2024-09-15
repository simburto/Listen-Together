#
# This file actually calls the function to authenticate the app with spotify, initialises the room managers, and starts the server
#

import RoomManager
import spotify


def main():
    spotify.authenticate_spotify_app()
    room_manager = RoomManager.RoomManager((1, 1000))
    room_managers = [room_manager]
