import time

import situation
import streamlit as st
from conversation import Context, Message, get_response

st.title("Чат")
st.write(f"### {situation.situation}")

if not st.button("Начать") and "messages" not in st.session_state:
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "turn" not in st.session_state:
    st.session_state.turn = "assistant"

# print(st.session_state.messages)
for message in st.session_state.messages:
    with st.chat_message(message.role):
        if message.role == "assistant":
            st.write(f"<details><summary>Analysis</summary>\n\n{message.explanation}\n\n---\n</details>{message.content}", unsafe_allow_html=True)
            continue
        st.write(message.content)



container = st.empty()

if prompt := st.chat_input("Say something"):
    st.session_state.messages.append(Message(role="user", content=prompt))
    st.session_state.turn = "assistant"
    st.rerun()


if st.session_state.turn == "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Печатает..."):
            context = Context(
                situation=situation.situation,
                player_role=situation.player_role,
                assistant_role=situation.assistant_role,
                assistant_role_description=situation.assistant_role_description,
                messages=st.session_state.messages,
            )
            response, explanation = get_response(context)
            # time.sleep(1)
            # response = "LOL"
        st.write(response)
    st.session_state.messages.append(
        Message(role="assistant", content=response, explanation=explanation)
    )
    st.session_state.turn = "user"
    st.rerun()
