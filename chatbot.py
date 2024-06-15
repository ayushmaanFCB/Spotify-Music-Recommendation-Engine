import streamlit as st
import time
import random


# def app():
#     st.markdown(
#         "<h1 style='text-align:center; color:#1cbc55'>CHAT WITH THE BOT</h1>", unsafe_allow_html=True)

#     st.warning("FEATURE STILL UNDER DEVLOPEMENT, SORRY FOR THE INCONVINIENCE")


def app():
    def response_generator():
        response = random.choice(
            [
                "Hello there! How can I assist you today?",
                "Hi, human! Is there anything I can help you with?",
                "Do you need help?",
            ]
        )
        for word in response.split():
            yield word + " "
            time.sleep(0.1)

    st.markdown(
        "<h1 style='text-align:center; color:#1cbc55'>CHAT TO KNOW MORE</h1>", unsafe_allow_html=True)

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
            response = st.write_stream(response_generator())
        st.session_state.messages.append(
            {"role": "assistant", "content": response})
