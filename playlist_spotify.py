from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
URL = os.getenv('URL')

print(CLIENT_ID, CLIENT_SECRET, URL)

def get_songs(date: str) -> dict:
    """Returns a dictionary of songs by artist based on the date."""
    response = requests.get(f'https://www.billboard.com/charts/hot-100/{date}')
    billboard_page = response.text

    soup = BeautifulSoup(billboard_page, "html.parser")

    songs = dict()

    class_titles = """o-chart-results-list-row-container"""
    rows = soup.find_all(name="div", class_=class_titles)

    for row in rows:
        label = row.find(
            "ul", class_="lrv-a-unstyle-list lrv-u-flex lrv-u-height-100p lrv-u-flex-direction-column@mobile-max")
        # Delete spaces with strip function
        title = label.find("h3").text.strip()
        author = label.find("span").text.strip()
        # Add to the dictionary of song
        songs[author] = title

    return songs


def connect_spotify() -> tuple:
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope="playlist-modify-private",
            redirect_uri=URL,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            show_dialog=True,
            cache_path="token.txt"
        )
    )
    return sp, sp.me()["id"]


def search_songs(sp, songs):
    song_uris = list()

    for artist, song in songs.items():

        search = sp.search(
            q=f'track:{song} artist:{artist}',
            limit=1,
            type='track'
        )

        try:
            uri = search["tracks"]["items"][0]["uri"]
            song_uris.append(uri)
        except IndexError:
            print(f"{song} doesn't exist in Spotify. Skipped.")

    print("--------------------------")
    return song_uris


def create_playlist(sp, id, song_uris):
    # Create blank playlist
    playlist_blank = sp.user_playlist_create(
        user=id,
        name="Your playlist, by Tukey 🦃",
        public=False
    )
    playlist_id = playlist_blank['id']

    # Add tracks
    sp.user_playlist_add_tracks(
        user=id,
        playlist_id=playlist_id,
        tracks = song_uris    
    )


def main():
    # Get the date to look for on the billboard page
    date = input(
        "Which day do you want to musical travel to? Type the date in this format YYYY-MM-DD: ")
    songs = get_songs(date)
    # Getting the ID of the user
    sp, id = connect_spotify()
    # Search songs on spotify
    song_uris = search_songs(sp, songs)
    # Create Playlist
    create_playlist(sp, id, song_uris)


main()
