import requests
from ytmusicapi import YTMusic


def getEmbed(artistname, trackname):
    ytmusic = YTMusic()
    search = ytmusic.search(artistname + trackname, filter="songs")
    songId = search[0]['videoId']
    return songId


def host(roomcode, ytpassword, ytip):  # if youtube ytclient is hosting
    # TODO: roomcode isn't used here
    output = []
    while len(output) == 0:
        try:  # tries to connect to local ytclient
            if ytpassword != 0:
                output = requests.get(url='http://' + ytip + ':9863/query',
                                      headers={f'Authorization': f'Bearer {ytpassword}'}).json()
            else:
                output = requests.get(url='http://' + ytip + ':9863/query').json()
        except requests.ConnectionError:
            return {
                'isHosting': False
            }
    if output['player']['hasSong'] == False:  # checks if player has a song
        returncode = [0]
        return returncode
    elif output['player']['isPaused'] == True:  # checks if song within player is paused
        returncode = [1]
        return returncode
    elif output['track']['author'] == 'Video will play after ad':  # check if song within player is an ad
        returncode = [2]
        return returncode
    else:  # filters output to only outputs needed (tracks, artist, and progress)
        trackname = output['track']['title']
        artistname = output['track']['author']
        position_ms = output['player']['seekbarCurrentPosition'] * 1000
        returncode = 3
        return returncode, trackname, artistname, position_ms
