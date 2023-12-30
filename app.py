import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import configparser
import track_info_generator
import playlist_generator
import ast

# st.set_page_config(layout='wide')

config = configparser.ConfigParser()
config.read('./configs/config.cfg')

SPOTIPY_CLIENT_ID = config.get('SPOTIFY', 'SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = config.get('SPOTIFY', 'SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = config.get('SPOTIFY', 'SPOTIPY_REDIRECT_URI')

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope='user-library-read'))
st.title("SPOTIFY RECOMMENDATION ENGINE")

search_query = st.text_input("ENTER ANY SONG NAME:")


if search_query:

    results = sp.search(q=search_query, type='track', limit=5)
    suggestions = [track['name'] for track in results['tracks']['items']]
    selected_song_index = st.selectbox("AVAILABLE SONGS:", range(
        len(suggestions)), format_func=lambda x: suggestions[x])

    number_of_songs = int(st.number_input(
        "NUMBER OF SONGS YOU WANT TO GENERATE", min_value=3, max_value=10))

    if st.button("GENERATE PLAYLIST"):

        st.markdown("<h2>Recommended Songs : </h2>", unsafe_allow_html=True)

        selected_track = results['tracks']['items'][selected_song_index]
        track_id = selected_track['id']

        song = track_info_generator.fetch_track_info(track_id)
        recommendations = playlist_generator.generate_playlist(
            [song], number_of_songs)
        recommendations = track_info_generator.apply_cover_images(
            recommendations)
        recommendations = recommendations[[
            'name', 'artists', 'release_date', 'explicit', 'duration_ms', 'album_cover']]

        print(recommendations)

        for index, row in recommendations.iterrows():
            artists = ast.literal_eval(row['artists'])
            artists = ', '.join(list(artists))
            song_card = """
                <div style="background-color: #121313; padding:15px; overflow:hidden">
                    <div style='display: inline-block; margin-right: 30px;'>
                            <h3>{1}</h3>
                            <h5>{2}</h5>
                    </div>
                    <img src='{0}' height=100px' style='float:right'>
                </div>
            """.format(row['album_cover'], row['name'], artists)

            st.write(song_card, unsafe_allow_html=True)
            st.divider()
else:
    st.success(
        "Enter a search query to get suggestions. A list of available options will be shown.")
