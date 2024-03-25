import streamlit as st
from keras.models import load_model
import cv2
import numpy as np
import playlist_generator
import track_info_generator
from colorama import init, Fore
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import configparser
import sys
import ast
import time
import json

try:
    loaded_model = load_model("./models/model_50epochs.h5")
    print(f"\n{Fore.GREEN}Emotion Detection Model has been loaded successfully !!!")
except:
    print(f"\n{Fore.RED}Failed to load the model, Please check the logs for issue.")


try:
    config = configparser.ConfigParser()
    config.read('./configs/config.cfg')

    SPOTIPY_CLIENT_ID = config.get('SPOTIFY', 'SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET = config.get('SPOTIFY', 'SPOTIPY_CLIENT_SECRET')
    SPOTIPY_REDIRECT_URI = config.get('SPOTIFY', 'SPOTIPY_REDIRECT_URI')

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))
    print(f"\n{Fore.GREEN}Connected to Spotify API succesfully !!!")

except Exception as e:
    print(f"\n{Fore.RED}Failed to connect to Spotify API, Try Re-Running the app....")
    sys.exit(1)


st.markdown(
    "<h1 style='text-align:center; color:#1cbc55'>YOUR MOOD, YOUR MUSIC</h1>", unsafe_allow_html=True)

# st.markdown("<h5 style='text-align:center'>The recommendation engine will scan your face and predict your mood, and accordingly will generate music library.</h5>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    number_of_songs = int(st.number_input(
        "NUMBER OF SONGS", min_value=3, max_value=15))
with col2:
    st.write("Restrict inappropriate tracks")
    explicit = st.toggle(label="Allow Explicit", value=True)

image_buffer = st.camera_input(
    label="Upload a snapshot of your face."
)

filt_col = ['acousticness', 'danceability',
            'energy', 'loudness', 'tempo', 'valence']

with open("./data/mood_parameters_narrow.json", "r") as file:
    mood_parameters = json.load(file)


if image_buffer is not None:
    bytes_data = image_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(
        bytes_data, np.uint8), cv2.IMREAD_GRAYSCALE)

    cv2_img = cv2.resize(cv2_img, (48, 48))
    cv2_img = np.expand_dims(cv2_img, axis=0) / 255

    predictions = loaded_model.predict(cv2_img)

    mood = np.argmax(predictions)
    mood_value = max(predictions[0])


    if mood == 0:
        mood_arr = mood_parameters["happy"]

    mood_input = {
        'acousticness': mood_arr[0],
        'danceability': mood_arr[1],
        'energy': mood_arr[2],
        'loudness': mood_arr[3],
        'tempo': mood_arr[4],
        'valence': mood_arr[5]
    }

    print(
        f"\n{Fore.CYAN}Detected Mood from the snapshot : {mood_str} \n Scores: {predictions[0]}")

    recommendations = playlist_generator.generate_playlist_from_mood(
        [mood_input], num_recommendations=number_of_songs, explicit=explicit)

    recommendations = track_info_generator.apply_cover_images(
        sp, recommendations)
    recommendations = track_info_generator.apply_preview_url(
        sp, recommendations)
    recommendations = recommendations[[
        'name', 'artists', 'release_date', 'explicit', 'duration_ms', 'album_cover', 'preview_url']]

    print(f"\n{Fore.LIGHTCYAN_EX}{recommendations}")

    st.markdown("<h3 style='text-align:center; color:#1cbc55'>RECOMMENDATIONS</h3>",
                unsafe_allow_html=True)

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
