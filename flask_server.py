import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, redirect, jsonify
import db_functions
import spotify_fetcher
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["https://accounts.spotify.com","https://spotify.com"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

load_dotenv()

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
FRONTEND_URL = os.getenv('URL')

sp_oauth = SpotifyOAuth(
    client_id,
    client_secret,
    redirect_uri,
    scope="playlist-read-private playlist-modify-public user-top-read user-read-email",
    show_dialog=True
)


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


token_info = None
headers = None


@app.route('/')
def index():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    global token_info, headers, userId, userName
    # Get the access token from the callback
    code = request.args.get('code')
    if not code:
        return redirect(f"{FRONTEND_URL}/login")

    token_info = sp_oauth.get_access_token(code)
    if not token_info:
        return redirect(f"{FRONTEND_URL}/login")

    token = token_info.get('access_token')
    if not token:
        return redirect(f"{FRONTEND_URL}/login")

    try:
        headers = get_auth_header(token)
        userId, userName = spotify_fetcher.getUsername(headers)
        return redirect(f"{FRONTEND_URL}/main")
    except Exception as e:
        print(f"Error during authentication: {e}")
        return redirect(f"{FRONTEND_URL}/login")


@app.route('/get_user_data', methods=['GET', 'POST'])
def get_user_data():
    global token_info
    if not token_info or 'access_token' not in token_info:
        return jsonify({"error": "Unauthorized"}), 401

    token = token_info['access_token']
    headers = get_auth_header(token)
    try:
        userId = spotify_fetcher.getUsername(headers)  # Fetched data
        print(userId)
    except Exception as e:
        return jsonify({"error": "Failed to fetch user data from Spotify", "details": str(e)}), 500

    user = db_functions.isUserExists((userId,))[0]
    print(user)

    if user:
        user_data = {
            "username": user['username'],
            "gender": user['gender'],
            "age": user['age'],
            "weight": user['weight'],
            "height": user['height'],
            "distance": user['distance'],
            "runningTime": user['runningTime']
        }
        return jsonify(user_data)
    else:
        return jsonify({"error": "User not found"}), 404


@app.route('/generate-playlist', methods=['POST'])
def generate_playlist():
    global token_info, headers, userId, userName
    if not token_info or 'access_token' not in token_info:
        return jsonify({"error": "Unauthorized"}), 401

    # Get data from inputs
    data = request.json
    age = data.get("age")
    gender = data.get("gender")
    weight = data.get("weight")
    height = data.get("height")
    distance = data.get("distance")
    duration = int(data.get("time")) * 60
    pace = data.get("pace")

    # Check if user already exists
    if db_functions.isUserExists((userId,))[0]:
        print("im updating")
        # Update userInfo
        userParametersForUpdate = (gender, age, weight, height, distance, duration, userId)
        db_functions.updateUserinfo(userParametersForUpdate)
    else:
        # Insert to userInfo
        userParametersForInsert = (userId, gender, age, weight, height, distance, duration)
        db_functions.insertUserinfo(userParametersForInsert)
    # Insert to playlists
    counter = 2
    playlistName = f"{userName}'s {pace} BPM playlist for {distance} KM"

    if db_functions.isPlaylistExists((playlistName,))[0]:
        newplaylistName = f"{playlistName}({counter})"

        while db_functions.isPlaylistExists((newplaylistName,))[0]:
            counter += 1
            newplaylistName = f"{playlistName}({counter})"
            print(newplaylistName)
        playlistName = newplaylistName

    playlist_duration, tracksList = spotify_fetcher.createPlaylist(headers, int(pace), duration)
    playlistParametersForInsert = (playlistName, userId, playlist_duration)
    db_functions.insertPlaylist(playlistParametersForInsert)

    # Get Playlist Id
    plsylistId = db_functions.selectLastPlaylist((userId,))

    # Add tracks to Db
    for track in tracksList:
        tracksParametersForInsert = (track['name'], track['artist'], track['duration'], plsylistId)
        db_functions.insertTracks(tracksParametersForInsert)

    return jsonify({"message": "Playlist generation started!"}), 200


@app.route('/get_playlists_data', methods=['GET', 'POST'])
def get_playlists_data():
    playlists_data = db_functions.selectPlaylists((userId,))
    return jsonify(({"playlists": playlists_data}))


@app.route('/remove_playlist', methods=['DELETE'])
def remove_playlist():
    playlist_id = request.args.get('id')
    db_functions.removePlaylist((playlist_id, userId))
    return jsonify({"message": "Playlist removed!"}), 200


@app.route('/get_playlists_tracks', methods=['GET', 'POST'])
def get_playlist_tracks():
    playlist_id = request.args.get('playlist_id')
    tracks_data = db_functions.selectTracks((playlist_id,))
    return jsonify(({"tracks": tracks_data}))


@app.route('/remove_track', methods=['DELETE'])
def remove_track():
    track_id = request.args.get('track_id')
    playlist_id = request.args.get('playlist_id')

    db_functions.removeTrack((track_id, playlist_id))
    return jsonify({"message": "Track removed!"}), 200


if __name__ == "__main__":
    app.run(port=1998)