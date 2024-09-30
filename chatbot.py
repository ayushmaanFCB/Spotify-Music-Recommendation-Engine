import streamlit as st
import time
import random
import os
from pandasai import Agent
import pandas as pd


# def app():
#     st.markdown(
#         "<h1 style='text-align:center; color:#1cbc55'>CHAT WITH THE BOT</h1>", unsafe_allow_html=True)

#     st.warning("FEATURE STILL UNDER DEVLOPEMENT, SORRY FOR THE INCONVINIENCE")


try:
    os.environ["PANDASAI_API_KEY"] = (
        "$2a$10$UWmuWvJnRiC6K2rc/RgS8.ECP5oDM07mkLF9lKqQxZRxDAV8eNYKu"
    )
except:
    st.warning("The Bot API is facing some issue, please try again later.")

try:
    df = pd.read_csv("./data/tracks.csv")
    agent = Agent(df)
    print("\nChatbot Agent is ready...")
except:
    st.warning("The Bot API is facing some issue, please try again later.")


def app():
    def response_generator(prompt):
        response = agent.chat(prompt)
        return response

    st.markdown(
        "<h1 style='text-align:center; color:#1cbc55'>CHAT TO KNOW MORE</h1>",
        unsafe_allow_html=True,
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = st.write(response_generator(prompt=prompt))
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    app()
