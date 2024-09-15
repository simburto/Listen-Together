from dataclasses import dataclass
from random import randint
from typing import Dict
import time

@dataclass
class Room:
    host_platform: str # "spotify" or "yt"
    auth_token: str
    position_ms: int = 0
    trackname: str = ""
    artistname: str = ""
    last_action_timestamp: float = time.time()

class RoomManager:
    rooms: Dict[int, Room] = {}

    # roomcode_range is inclusive (includes both endpoints)
    def __init__(self, roomcode_range: tuple[int, int]):
        self.roomcode_range = roomcode_range


    def create_room(self, host_platform: str, auth_token: str, position_ms: int) -> None:
        roomcode = randint(self.roomcode_range[0], self.roomcode_range[1])
        attempts = 0
        while roomcode in self.rooms:
            roomcode = randint(self.roomcode_range[0], self.roomcode_range[1])
            attempts += 1
            if attempts > 200:
                raise Exception("Exceeded 200 attempts to generate a unique roomcode")
        self.rooms[roomcode] = Room(host_platform, auth_token, position_ms)


    def update(self):
        """Deletes inactive rooms and updates the current song and position for each room"""
        for roomcode, room in self.rooms.items():
            if time.time() - room.last_action_timestamp > 60:
                del self.rooms[roomcode]
                print(f"Room {roomcode} has been deleted due to inactivity")
