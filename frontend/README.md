# Frontend

The frontend server uses a separate .env file:
```
NEXTAUTH_SECRET=
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
```
`NEXTAUTH_SECRET` is a random string, generated with the `openssl rand -base64 32` command. Its purpose is to hash tokens, sign/encrypt cookies and generate cryptographic keys.
`SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` are for the Spotify Developer OAuth handling. They are identical to the backend.

## Scopes used
* App remote control
* Streaming
* User modify playback state
* User read currently playing
* User read playback state
