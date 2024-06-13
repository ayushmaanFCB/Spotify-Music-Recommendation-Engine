import streamlit as st
from streamlit_option_menu import option_menu
import from_emotion
import from_song
import chatbot

st.set_page_config(layout='wide')


def main_page():
    from_song.app()


def emotion_page():
    from_emotion.app()


def chatbot_page():
    chatbot.app()


with st.sidebar:
    selected = option_menu("Menu", ["Tracks by Vibe", "Music for your Mood", "Ask the Bot"],
                           icons=["bi-music-note-list",
                                  "bi-emoji-smile", "bi-robot"],
                           menu_icon="bi-spotify", default_index=0)

if selected == "Tracks by Vibe":
    main_page()
elif selected == "Music for your Mood":
    emotion_page()
elif selected == "Ask the Bot":
    chatbot_page()
