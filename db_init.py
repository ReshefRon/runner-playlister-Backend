import sqlite3 as sql

conn = sql.connect("Database/runnerplaylister.db")

c = conn.cursor()


# Create USER_INFO table
c.execute('''
CREATE TABLE USER_INFO (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    gender TEXT,
    age INTEGER,
    weight REAL,
    height REAL,
    distance REAL,
    runningTime INTEGER
)
''')

# Create PLAYLISTS table
c.execute('''
CREATE TABLE PLAYLISTS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT NOT NULL,
    duration INTEGER,
    createdTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES USER_INFO(username)
)
''')

# Create TRACKS table
c.execute('''
CREATE TABLE TRACKS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    artist TEXT NOT NULL,
    duration INTEGER,
    playlist_id INTEGER,
    FOREIGN KEY (playlist_id) REFERENCES PLAYLISTS(id)
)
''')