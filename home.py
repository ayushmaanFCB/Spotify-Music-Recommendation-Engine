import streamlit as st
from streamlit_option_menu import option_menu
# import from_emotion
# import from_song

st.set_page_config(layout='wide')


# def main_page():
#     from_song.app()


# def emotion_page():
#     from_emotion.app()


with st.sidebar:
    selected = option_menu("Menu", ["Track by Vibe", "Music for your Mood", "Ask the Bot"],
                           icons=["bi-music-note-list",
                                  "bi-emoji-smile", "bi-robot"],
                           menu_icon="bi-spotify", default_index=0)

# if selected == "Main":
#     main_page()
# elif selected == "Emotion":
#     emotion_page()
