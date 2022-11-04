import requests
import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URL = "http://localhost:8888/callback"

date = input("Which year do you want to travel to? Type the date in the format YYYY-MM-DD: ")

response = requests.get(url=f"https://www.billboard.com/charts/hot-100/{date}/")
billboard = response.text
soup = BeautifulSoup(billboard, "html.parser")
song_titles = soup.select(selector="li #title-of-a-story")
top_100_songs = [song.getText().strip() for song in song_titles]

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri=REDIRECT_URL,
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        show_dialog=True,
        cache_path="venv/token.txt"
    )
)

user_id = sp.current_user()["id"]

song_uris = []
year = date.split("-")[0]
for song in top_100_songs:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

playlist = sp.user_playlist_create(user=user_id, name=f"Billboard Mixtape ({date})", public=False)

sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
