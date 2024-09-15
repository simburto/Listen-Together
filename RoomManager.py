from dataclasses import dataclass
from random import randint

@dataclass
class Room:
    roomcode: int
    host_platform: str # "spotify" or "yt"
    auth_token: str
    position_ms: int = 0
    trackname: str = ""
    artistname: str = ""

class RoomManager:
    rooms = []

    # roomcode_range is inclusive (includes both endpoints)
    def __init__(self, roomcode_range: tuple[int, int]):
        self.roomcode_range = roomcode_range

    def create_room(self, host_platform: str, auth_token: str, position_ms: int) -> None:
        roomcode = randint(self.roomcode_range[0], self.roomcode_range[1])
        while roomcode in
        self.rooms.append(Room(roomcode, host_platform, auth_token, position_ms))
