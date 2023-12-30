import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import configparser
import track_info_generator
import playlist_generator

st.set_page_config(layout='wide')

config = configparser.ConfigParser()
config.read('./configs/config.cfg')

SPOTIPY_CLIENT_ID = config.get('SPOTIFY', 'SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = config.get('SPOTIFY', 'SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = config.get('SPOTIFY', 'SPOTIPY_REDIRECT_URI')

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope='user-library-read'))
st.title("PLAYLIST GENERATOR")

search_query = st.text_input("ENTER SONG NAME:")

if search_query:
    results = sp.search(q=search_query, type='track', limit=5)
    suggestions = [track['name'] for track in results['tracks']['items']]
    selected_song_index = st.selectbox("AVAILABLE SONGS:", range(
        len(suggestions)), format_func=lambda x: suggestions[x])

    if st.button("GENERATE PLAYLIST"):
        selected_track = results['tracks']['items'][selected_song_index]
        track_id = selected_track['id']

        song = track_info_generator.fetch_track_info(track_id)
        recommendations = playlist_generator.generate_playlist([song])
        recommendations = track_info_generator.apply_cover_images(
            recommendations)
        recommendations = recommendations[[
            'name', 'artists', 'release_date', 'explicit', 'duration_ms', 'album_cover']]

        st.data_editor(
            recommendations,
            column_config={
                "album_cover": st.column_config.ImageColumn(
                    label=None, help="Streamlit app preview screenshots"
                )
            },
            hide_index=True,
        )
else:
    st.warning("Enter a search query to get suggestions.")
