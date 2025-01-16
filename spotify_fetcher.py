from requests import post, get
import random

search_url = "https://api.spotify.com/v1/search"
tracks = []
total_tracks_duration = 0
AMOUNT = 0

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
    global AMOUNT

    if duration < 600:
        AMOUNT = 1
    elif duration < 1200:
        AMOUNT = 2
    elif duration < 1800:
        AMOUNT = 3
    elif duration < 2400:
        AMOUNT = 4
    else:
        AMOUNT = 5

    addUserTopTracks(headers)
    addTopHitsTracks(headers)
    addBpmTracks(headers, bpm, duration - total_tracks_duration)

    return total_tracks_duration,tracks





def addUserTopTracks(headers):
    global total_tracks_duration
    global AMOUNT

    query_url = f"https://api.spotify.com/v1/me/top/tracks?limit={AMOUNT}"
    result = get(query_url, headers=headers)
    try:
        json_result_UserTopTracks=result.json()["items"]
        for track in json_result_UserTopTracks:
            tracks.append({
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "duration": round(int(track["duration_ms"]) / 1000)
            })
            total_tracks_duration += round(int(track["duration_ms"]) / 1000)
    except Exception as e:
        print(e)




def addTopHitsTracks(headers):
    global total_tracks_duration
    global AMOUNT

    query_url = "https://api.spotify.com/v1/playlists/3Oh3oSaZjfsXcNwSpVMye2/tracks"
    result = get(query_url, headers=headers)
    try:
        json_result_topHits = result.json()["items"]
        for item in json_result_topHits[:AMOUNT]:
            tracks.append({
                "name": item["track"]["name"],
                "artist": item["track"]["artists"][0]["name"],
                "duration": round(int(item["track"]["duration_ms"]) / 1000)
            })
            total_tracks_duration += round(int(item["track"]["duration_ms"]) / 1000)

    except Exception as e:
        print(e)


def addBpmTracks(headers, bpm, duration):
    global total_tracks_duration

    playlist_ids = []
    query = f"?q=%22running%20{bpm}%20bpm%22&type=playlist&limit=10"
    query_url = search_url + query
    result = get(query_url, headers=headers)
    try:
        json_result_playlists = result.json()["playlists"]["items"]
        for item in json_result_playlists:
            if item is not None:
                playlistName = item["name"].lower()
                if ("running" in playlistName) and ("bpm" in playlistName) and (str(bpm) in playlistName):
                    playlist_ids.append(item["id"])
    except Exception as e:
        print(e)

    bpm_temp_list = []
    for id in playlist_ids:
        query_url = f"https://api.spotify.com/v1/playlists/{id}/tracks"
        result = get(query_url, headers=headers)
        try:
            json_result_playlistTracks = result.json()["items"]
            for item in json_result_playlistTracks:
                bpm_temp_list.append({
                    "name": item["track"]["name"],
                    "artist": item["track"]["artists"][0]["name"],
                    "duration": round(int(item["track"]["duration_ms"])/1000)
                })
                #popularity = item["track"]["popularity"]    //OPTIONAL: for future features
        except Exception as e:
            print(e)

    total_duration = 0
    while total_duration < duration:
        track = random.choice(bpm_temp_list)
        total_duration += track["duration"]
        total_tracks_duration +=  track["duration"]
        tracks.append(track)



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






