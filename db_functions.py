import sqlite3 as sql

def get_db_connection():
    conn = sql.connect("Database/runnerplaylister.db")
    c = conn.cursor()
    return conn, c

#Check if user exists
def isUserExists(params):
    conn, c = get_db_connection()

    c.execute('''
        SELECT COUNT(id)
        FROM USER_INFO
        WHERE username=?
        ''', params)

    result = c.fetchone()
    conn.close()
    return result

#Insert user info
def insertUserinfo(params):
    conn, c = get_db_connection()

    c.execute('''
    INSERT INTO USER_INFO (username, gender, age, weight, height, distance, runningTime)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', params)

    conn.commit()
    conn.close()

# Update user info
def updateUserinfo(params):
    conn, c = get_db_connection()

    c.execute('''
    UPDATE USER_INFO 
    SET gender = ?,
        age = ?,
        weight = ?,
        height = ?,
        distance = ?,
        runningTime = ?
    WHERE username = ?
    ''', params)

    conn.commit()
    conn.close()


#Insert playlist
def insertPlaylist(params):
    conn, c = get_db_connection()

    c.execute('''
    INSERT INTO PLAYLISTS (name, username, duration)
    VALUES (?, ?, ?)
    ''', params)  # duration in seconds

    conn.commit()
    conn.close()


#Remove playlist
def removePlaylist(params):
    conn, c = get_db_connection()

    c.execute('''
    DELETE FROM TRACKS 
    WHERE playlist_id = ?
    ''', (params[0],))



    # Then remove the playlist itself
    c.execute('''
    DELETE FROM PLAYLISTS 
    WHERE id = ? AND username = ?
    ''', params)

    conn.commit()
    conn.close()

#Insert tracks
def insertTracks(params):
    conn, c = get_db_connection()

    c.execute('''
    INSERT INTO TRACKS (name, artist, duration, spotify_track_id, playlist_id)
    VALUES (?, ?, ?, ?, ?)
    ''', params)

    conn.commit()
    conn.close()



#Remove track
def removeTrack(params):
    conn, c = get_db_connection()

    c.execute('''
        SELECT duration
        from TRACKS
        WHERE id = ? and playlist_id =?
        ''', (params[0], params[1]))

    result = c.fetchone()

    c.execute('''
    DELETE FROM TRACKS 
    WHERE id = ? and playlist_id =?
    ''', (params[0], params[1]))

    c.execute('''
        UPDATE PLAYLISTS
        SET duration = duration - ?
        WHERE id = ?
        ''', (result[0], params[1]))

    conn.commit()
    conn.close()


#Extract PlaylistId
def selectLastPlaylist(params):
    conn, c = get_db_connection()

    c.execute('''
       SELECT MAX(id)
       FROM PLAYLISTS p
       WHERE p.username = ?
       ''', params)
    result = c.fetchone()
    if result:
        last_playlist_id = result[0]
    else:
        last_playlist_id = None

    conn.close()
    return last_playlist_id

#Check if playlist exists
def isPlaylistExists(params):
    conn, c = get_db_connection()

    c.execute('''
        SELECT COUNT(id)
        FROM PLAYLISTS p
        WHERE p.name = ?
        ''', params)

    result = c.fetchone()
    conn.close()
    return result


#Select playlist by username
def selectPlaylists(params):
    conn, c = get_db_connection()

    c.execute('''
    SELECT id, name, duration, createdTime 
    FROM PLAYLISTS p
    WHERE p.username = ?
    ''', params)

    result = c.fetchall()
    conn.close()
    return result




#Select track by playlist_id
def selectTracks(params):
    conn, c = get_db_connection()

    c.execute('''
    SELECT id, name, artist, duration, spotify_track_id FROM TRACKS 
    WHERE playlist_id = ?
    ORDER BY name
    ''', params)

    result = c.fetchall()
    conn.close()
    return result




