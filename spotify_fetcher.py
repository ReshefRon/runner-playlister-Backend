from requests import post, get
import random

search_url = "https://api.spotify.com/v1/search"
tracks = []
total_tracks_duration = 0


def getUsername(headers):
    query_url = "https://api.spotify.com/v1/me"
    result = get(query_url, headers=headers)
    try:
        username = result.json()["display_name"]
        userEmail = result.json()["email"]
        return userEmail,username
    except Exception as e:
        print(e)


def createPlaylist(headers, bpm, duration):
    global total_tracks_duration

    addUserTopTracks(headers)
    addTopHitsTracks(headers)
    print(tracks)
    addBpmTracks(headers, bpm, duration - total_tracks_duration)

    return total_tracks_duration, tracks





def addUserTopTracks(headers):
    global total_tracks_duration

    query_url = f"https://api.spotify.com/v1/me/top/tracks?limit=1"
    result = get(query_url, headers=headers)
    try:
        json_result_UserTopTracks=result.json()["items"]
        for track in json_result_UserTopTracks:
            tracks.append({
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "duration": round(int(track["duration_ms"]) / 1000),
                "spotify_track_id": track["id"]
            })
            total_tracks_duration += round(int(track["duration_ms"]) / 1000)
    except Exception as e:
        print(e)




def addTopHitsTracks(headers):
    global total_tracks_duration

    query_url = "https://api.spotify.com/v1/playlists/3Oh3oSaZjfsXcNwSpVMye2/tracks"
    result = get(query_url, headers=headers)
    try:
        json_result_topHits = result.json()["items"]["track"]
        for item in json_result_topHits[:2]:
            tracks.append({
                "name": item["track"]["name"],
                "artist": item["track"]["artists"][0]["name"],
                "duration": round(int(item["track"]["duration_ms"]) / 1000),
                "spotify_track_id": item["track"]["id"]
            })
            total_tracks_duration += round(int(item["track"]["duration_ms"]) / 1000)

    except Exception as e:
        print(e)


def addBpmTracks(headers, bpm, remaining_duration):
    global total_tracks_duration
    global tracks


    playlist_ids = []
    query = f"?q=%22running%20{bpm}%20bpm%22&type=playlist&limit=20"  # Increased to 20
    query_url = search_url + query
    result = get(query_url, headers=headers)

    added_songs = {(track["name"], track["artist"]) for track in tracks}

    try:
        json_result_playlists = result.json()["playlists"]["items"]
        for item in json_result_playlists:
            if item is not None:
                playlistName = item["name"].lower()
                if ("running" in playlistName) and ("bpm" in playlistName) and (str(bpm) in playlistName):
                    playlist_ids.append(item["id"])
    except Exception as e:
        print(f"Error finding playlists: {e}")
        return False

    all_available_tracks = []

    # Collect all tracks first
    for playlist_id in playlist_ids:
        query_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        try:
            result = get(query_url, headers=headers)
            json_result_playlistTracks = result.json()["items"]

            for item in json_result_playlistTracks:
                if (item["track"] is not None and
                        item["track"]["name"] and
                        item["track"]["artists"] and
                        item["track"]["duration_ms"]):

                    name = item["track"]["name"].strip()
                    artist = item["track"]["artists"][0]["name"].strip()

                    if not name or not artist:
                        continue

                    if (name, artist) not in added_songs:
                        track_data = {
                            "name": name,
                            "artist": artist,
                            "duration": round(int(item["track"]["duration_ms"]) / 1000),
                            "spotify_track_id": item["track"]["id"]
                        }
                        all_available_tracks.append(track_data)
                        added_songs.add((name, artist))

        except Exception as e:
            print(f"Error getting tracks from playlist {playlist_id}: {e}")
            continue

    # Shuffle all available tracks
    random.shuffle(all_available_tracks)

    # Keep adding tracks until we exceed the duration
    current_duration = 0
    while current_duration < remaining_duration and all_available_tracks:
        track = all_available_tracks.pop()
        tracks.append(track)
        current_duration += track["duration"]
        total_tracks_duration += track["duration"]
    return True

def addFavArtistsTracks(headers, favArtists):
    global total_tracks_duration

    artist_ids = []
    for artist in favArtists:
        query = f"?q={artist}&type=artist&limit=1"
        query_url = search_url + query
        result = get(query_url, headers=headers)
        try:
            json_result_for_artist = result.json()['artists']["items"]
            if json_result_for_artist:
                artist_ids.append(json_result_for_artist[0]["id"])
        except Exception as e:
            print(f"Error fetching artist {artist}: {e}")
            continue
    favourite_artists_top_tracks = {}
    for artist_id in artist_ids:
        query_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=IL"
        result = get(query_url, headers=headers)
        try:
            json_result_for_track = result.json()["tracks"]
            for track in json_result_for_track:
                track_name = track["name"]
                track_id = track["id"]
                track_duration = track["duration_ms"]
                favourite_artists_top_tracks[track_name] = (track_id, track_duration)
        except Exception as e:
            print(f"Could not fetch top tracks for artist ID {artist_id}: {e}")
            continue

def create_spotify_playlist(headers, playlist_name, tracks):
    # Get user profile
    query_url = "https://api.spotify.com/v1/me"
    result = get(query_url, headers=headers)
    user_id = result.json()["id"]

    # Create empty playlist
    create_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    playlist_data = {
        "name": playlist_name,
        "description": "Created by RunnerPlaylister",
        "public": True
    }
    result = post(create_url, headers=headers, json=playlist_data)
    playlist_id = result.json()["id"]

    # Use stored track IDs directly
    track_uris = [f"spotify:track:{track[4]}" for track in tracks if
                  track[4]]  # Assuming track[4] is spotify_track_id

    # Add tracks to playlist in batches of 100
    if track_uris:
        add_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        for i in range(0, len(track_uris), 100):
            batch = track_uris[i:i + 100]
            post(add_url, headers=headers, json={"uris": batch})

    return playlist_id




