import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import configparser
import track_info_generator
import playlist_generator
import ast
from colorama import init, Fore
import time
import pickle
from datetime import datetime
import os
import sys

init(autoreset=True)

st.set_page_config(layout='wide')

if os.path.exists("./.cache"):
    os.remove("./.cache")

try:
    config = configparser.ConfigParser()
    config.read('./configs/config.cfg')

    SPOTIPY_CLIENT_ID = config.get('SPOTIFY', 'SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET = config.get('SPOTIFY', 'SPOTIPY_CLIENT_SECRET')
    SPOTIPY_REDIRECT_URI = config.get('SPOTIFY', 'SPOTIPY_REDIRECT_URI')

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

    sp_oauth = SpotifyOAuth(
        SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope='user-library-read user-read-private user-read-email playlist-read-private user-library-modify user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control playlist-modify-private playlist-modify-public')
    token_info = sp_oauth.get_cached_token()
    auth_url = sp_oauth.get_authorize_url()

    print(f"\n{Fore.GREEN}Connected to Spotify API succesfully !!!")

except Exception as e:
    print(f"\n{Fore.RED}Failed to connect to Spotify API, Try Re-Running the app....")
    sys.exit(1)


st.markdown(
    "<h1 style='text-align:center; color:#1cbc55'>SPOTIFY RECOMMENDATION ENGINE</h1>", unsafe_allow_html=True)


if "code" in st.experimental_get_query_params():
    a_code = st.experimental_get_query_params()["code"]
    token_info = sp_oauth.get_access_token(a_code)

    if token_info:
        sp1 = spotipy.Spotify(auth=token_info['access_token'])

        with open("./cache/recommendations.pkl", 'rb') as file:
            recommended_playlist = pickle.load(file)
        with open("./cache/query.pkl", 'rb') as file:
            query_song = pickle.load(file)

        playlist_name = 'Songs from Recommendation Engine'
        playlist_description = f'The following songs were recommended by the Spotify Recommendation Engine for <span style="color:#1cbc55">{query_song["name"]}</span> - {", ".join(query_song["artists"])} on {str(datetime.now().date())} at {str(datetime.now().hour)}:{str(datetime.now().minute)}:{str(datetime.now().second)}.'
        user_id = sp1.me()['id']

        playlist = sp1.user_playlist_create(
            user_id, playlist_name, public=True, description=playlist_description)
        playlist_id = playlist['id']

        tracks_to_add = ["spotify:track:" +
                         id for id in recommended_playlist['id']]
        sp1.playlist_add_items(playlist_id, tracks_to_add)

        c4, c5, c6 = st.columns([0.3, 1, 0.3])
        with c5:
            playlist_card = f"""
            <div style="background-color: #121313; padding:30px; margin-bottom:20px; border-radius: 50px; ">
                <div>
                    <img src='{sp1.me()['images'][1]['url']}'
                        style='height:100px; border-radius: 50%; display: inline-block; margin-right: 30px;'>
                    <div style="display: inline-block; vertical-align: top;">
                        <h4 >Hello <span style='color:#1cbc55'>{sp1.me()['display_name']}</span>, </h4>
                        <h5>Here's your new Spotify playlist</h5>
                    </div>
                </div>
                <h5 style='margin-top:30px; text-align:center'>{playlist['name']}</h5>
                <ul>
            """
            for index, row in recommended_playlist.iterrows():
                playlist_card = playlist_card + \
                    f"<li><a style='color:#1cbc55; text-decoration: none;' href='{row['preview_url']}'>{row['name']}</a> - {', '.join(list(ast.literal_eval(row['artists'])))}</li>"
            playlist_card = playlist_card + \
                f"</ul><p style='text-align:justify; margin-top:40px;'>{playlist['description']}</p></div><div style='text-align:center'><a href='/' target='_self'><button style='background-color: transparent; border: 2px solid #1cbc55; color: #1cbc55; padding: 10px 20px; cursor: pointer;'>GO BACK TO RECOMMENDATION ENGINE</button></a></div>"
            st.markdown(playlist_card, unsafe_allow_html=True)
        st.toast(
            "Authentication completed successfully, Playlist has been added to user Library", icon='✅')

    else:
        st.warning("AUTHENTICATION HAS FAILED")

else:
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        search_query = st.text_input("SEARCH FOR SONG")

    if search_query:

        results = sp.search(q=search_query, type='track', limit=5)
        suggestions = [track['name'] for track in results['tracks']['items']]
        display_suggestions = []
        for result in results['tracks']['items']:
            display_suggestions.append(
                result['name'] + " - " + result['artists'][0]['name'])

        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1:
            selected_song_index = st.selectbox("AVAILABLE SONGS", range(
                len(suggestions)), format_func=lambda x: display_suggestions[x])
        with col2:
            number_of_songs = int(st.number_input(
                "NUMBER OF SONGS", min_value=3, max_value=15))
        with col3:
            st.write("Restrict inappropriate tracks")
            explicit = st.toggle(label="Allow Explicit", value=True)
        with col4:
            search_but = st.button("GENERATE PLAYLIST",
                                   use_container_width=True)

        m_col1, m_col2 = st.columns([2, 1], gap='large')

        if search_but:
            with m_col1:
                selected_track = results['tracks']['items'][selected_song_index]
                track_id = selected_track['id']

                song = track_info_generator.fetch_track_info(sp, track_id)
                recommendations = playlist_generator.generate_playlist(
                    [song], number_of_songs, explicit)
                recommendations = track_info_generator.apply_cover_images(
                    sp, recommendations)
                recommendations = track_info_generator.apply_preview_url(
                    sp, recommendations)

                with open("./cache/recommendations.pkl", 'wb') as file:
                    pickle.dump(recommendations, file)
                with open("./cache/query.pkl", 'wb') as file:
                    pickle.dump(song, file)

                recommendations = recommendations[[
                    'name', 'artists', 'release_date', 'explicit', 'duration_ms', 'album_cover', 'preview_url']]

                print(f"\n{Fore.CYAN}{recommendations}\n")

                st.markdown(
                    "<h3 style='text-align:center; color:#1cbc55'>RECOMMENDATIONS</h3>", unsafe_allow_html=True)

                for index, row in recommendations.iterrows():
                    artists = ast.literal_eval(row['artists'])
                    artists = ', '.join(list(artists))
                    duration = track_info_generator.convert_msTo_min(
                        row['duration_ms'])
                    song_card = """
                        <div style="background-color: #121313; padding:30px; overflow:hidden; margin-bottom:20px; border-radius: 30px;">
                            <div style='display: inline-block; margin-right: 30px;'>
                                    <h5 style='color:#1cbc55'>{1}</h5>
                                    <h6>{2}</h6>
                                    <p>Release Date : {4}</p>
                                    <p>Duration : {5}</p>
                                    <audio controls>
                                        <source src="{3}" type="audio/mp3">
                                    </audio>
                            </div>
                            <div style='float:right'>
                                <img src='{0}' height='150px' >
                    """.format(row['album_cover'], row['name'], artists, row['preview_url'], row['release_date'], duration)
                    if row['explicit'] == 0:
                        song_card = song_card + "</div></div>"
                    else:
                        song_card = song_card + "<br><img src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAACXBIWXMAAAsTAAALEwEAmpwYAAABEUlEQVR4nO2WQWoCQRBFeym5QNQuRzyD69zATbA/uAu4MHogF1noIQSzqUIvkOQCOmeJlKARnBmTocYJjh9q1fBfz+9m+jtXabXXL7UWY+IFUxK8WYx6NQVj9U6FkuDLMzZewswOHGaew1a9E+G6K4U2Fr0H6yTVU+FewuvZokaiu7OGHv0Zc2WcLRyiKQpMaf5Z4PYadWK8e8bHpSHBsxmYGEMSfP9mPGNkBvaM0Yl55i1uSf+pELDLKbqD/xp1tEI3adwFkcHlSpzbBUdlRe1yiu7gf/3LpLIeiY4MHonD8urPooUozb+06tPcl72wLazsCeLE8/+pt/s2aFtvBTFx+Mzs1lpBrQu9fmkqtDLaARzjPmj2d5gbAAAAAElFTkSuQmCC' style='margin-top: 25px; float:right'></div></div>"

                    with st.expander(row['name']+" - "+artists):
                        st.write(song_card, unsafe_allow_html=True)

                    time.sleep(0.75)

                st.link_button(label="ADD TO PLAYLIST",
                               url=auth_url, use_container_width=True)

            with m_col2:
                st.markdown(
                    f"""<h3 style='text-align:center; color:#1cbc55'>SONG INFO</h3>
                        <div style="background-color: #121313; padding:30px; overflow:hidden; margin-bottom:20px; text-align:center; border-radius: 50px;">
                            <img src='{track_info_generator.generate_additional_info(sp, track_id)[0]}' height=150px>
                            <h5 style='color:#1cbc55; margin-top:10px'>{song['name']}</h5>
                            <h6>{', '.join(list(song['artists']))}</h6>
                            <p>Release Date : {song['release_date']}</p>
                            <p>Duration : {track_info_generator.convert_msTo_min(song['duration_ms'])}</p>
                            <audio controls>
                                <source src="{track_info_generator.generate_additional_info(sp, track_id)[1]}" type="audio/mp3">
                            </audio>
                        </div>
                    """, unsafe_allow_html=True)

    else:
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            st.success(
                "Enter a search query to get suggestions. A list of available options will be shown.")
