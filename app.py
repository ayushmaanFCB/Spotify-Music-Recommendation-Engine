import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import configparser
import track_info_generator
import playlist_generator
import ast
from colorama import init, Fore
import time

init(autoreset=True)

# st.set_page_config(layout='wide')

try:
    config = configparser.ConfigParser()
    config.read('./configs/config.cfg')

    SPOTIPY_CLIENT_ID = config.get('SPOTIFY', 'SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET = config.get('SPOTIFY', 'SPOTIPY_CLIENT_SECRET')
    SPOTIPY_REDIRECT_URI = config.get('SPOTIFY', 'SPOTIPY_REDIRECT_URI')

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope='user-library-read'))
except Exception as e:
    print(f"\n{Fore.RED}Failed to connect to Spotify API, check credentials...")


st.title("SPOTIFY RECOMMENDATION ENGINE")

search_query = st.text_input("SEARCH FOR SONG")


if search_query:

    results = sp.search(q=search_query, type='track', limit=5)
    suggestions = [track['name'] for track in results['tracks']['items']]
    display_suggestions = []
    for result in results['tracks']['items']:
        display_suggestions.append(
            result['name'] + " - " + result['artists'][0]['name'])

    col1, col2, col3 = st.columns([2.5, 1, 1])
    with col1:
        selected_song_index = st.selectbox("AVAILABLE SONGS", range(
            len(suggestions)), format_func=lambda x: display_suggestions[x])
    with col2:
        number_of_songs = int(st.number_input(
            "NUMBER OF SONGS", min_value=3, max_value=10))
    with col3:
        search_but = st.button("GENERATE PLAYLIST")

    if search_but:
        selected_track = results['tracks']['items'][selected_song_index]
        track_id = selected_track['id']

        song = track_info_generator.fetch_track_info(sp, track_id)
        recommendations = playlist_generator.generate_playlist(
            [song], number_of_songs)
        recommendations = track_info_generator.apply_cover_images(
            sp, recommendations)
        recommendations = track_info_generator.apply_preview_url(
            sp, recommendations)
        recommendations = recommendations[[
            'name', 'artists', 'release_date', 'explicit', 'duration_ms', 'album_cover', 'preview_url']]

        print(f"\n{Fore.CYAN}{recommendations}\n")

        st.markdown(
            "<h2 style='text-align:center'>Recommended Songs  </h2>", unsafe_allow_html=True)

        for index, row in recommendations.iterrows():
            artists = ast.literal_eval(row['artists'])
            artists = ', '.join(list(artists))
            duration = track_info_generator.convert_msTo_min(
                row['duration_ms'])
            song_card = """
                <div style="background-color: #121313; padding:15px; overflow:hidden; margin-bottom:20px">
                    <div style='display: inline-block; margin-right: 30px;'>
                            <h5>{1}</h5>
                            <h6>{2}</h6>
                            <p>Released On : {4}</p>
                            <audio controls>
                                <source src="{3}" type="audio/mp3">
                            </audio>
                    </div>
                    <div style='display: inline-block; vertical-align: top;'>
                        <p>Duration - {5}</p>
                    </div>
                    <img src='{0}' height=150px' style='float:right'>
                </div>
            """.format(row['album_cover'], row['name'], artists, row['preview_url'], row['release_date'], duration)

            with st.expander(row['name']+" - "+artists):
                st.write(song_card, unsafe_allow_html=True)

            time.sleep(0.75)
else:
    st.success(
        "Enter a search query to get suggestions. A list of available options will be shown.")
