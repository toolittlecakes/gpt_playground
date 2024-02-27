import json
import time
import uuid

from situation import situation
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from conversation import Context, Message, get_feedback, get_response

if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4()

if "situation" not in st.session_state:
    st.session_state.situation = situation.model_copy()
# st.session_state.situation = situation.model_copy()

st.title("Чат")

st.session_state.situation.description = st.text_area(
    "**Ситуация**", value=st.session_state.situation.description
)
# if st.checkbox("Посмотреть описание агрессора"):
# if st.toggle("Показать инструкцию агрессора", disabled=True):
if st.toggle("Показать инструкцию агрессора"):
    st.session_state.situation.assistant_role_description = st.text_area(
        "**Инструкция агрессора**",
        value=st.session_state.situation.assistant_role_description,
    )


if not st.button("Начать") and "messages" not in st.session_state:
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = [
        Message(role="assistant", content=st.session_state.situation.first_phrase)
    ]
    # hack
    # st.session_state.messages.append(
    #     Message(role="user", content="Чувствуешь, что я тебя недооцениваю, давая такую задачу?")
    # )
    # st.session_state.messages.append(
    #     Message(
    #         role="assistant",
    #         content="I get that maybe you have to cater to all skill levels here, but I thought you'd recognize my progress and tailor the challenges accordingly.",
    #     )
    # )
    # st.session_state.messages.append(
    #     Message(
    #         role="user",
    #         content="Well, I would also feel annoyed if had felt like my skills are not really improving. At the same time, it's important for me to have my students believe me and commit to my orders. If you are not ready for it, you can tell me directly, I will understand",
    #     )
    # )
    # st.session_state.messages.append(
    #     Message(role="user", content="Do you feel underestimated because of this task?")
    # )
    # st.session_state.messages.append(
    #     Message(
    #         role="assistant",
    #         content="I get that maybe you have to cater to all skill levels here, but I thought you'd recognize my progress and tailor the challenges accordingly.",
    #     )
    # )
    # st.session_state.messages.append(
    #     Message(
    #         role="user",
    #         content="Well, I would also feel annoyed if had felt like my skills are not really improving. At the same time, it's important for me to have my students believe me and commit to my orders. If you are not ready for it, you can tell me directly, I will understand",
    #     )
    # )

if "turn" not in st.session_state:
    st.session_state.turn = (
        "user" if st.session_state.messages[-1].role == "assistant" else "assistant"
    )


# print(st.session_state.messages)
for message in st.session_state.messages:
    with st.chat_message(message.role):
        if message.explanation:
            with stylable_container(
                "codeblock",
                """
                code {
                    white-space: pre-wrap !important;
                }
                """,
            ):
                st.write(
                    # f"<details open><summary>Analysis</summary><blockquote>\n\n{message.explanation}</blockquote></details>{message.content}",
                    # message.enriched_content,
                    message.enriched_content,
                    unsafe_allow_html=True,
                )
            continue
        st.write(message.content)

with st.container():
    col1, col2, *_ = st.columns(6)
    with col1:
        if st.button("Удалить", key="delete_last_message"):
            st.session_state.messages.pop()
            st.rerun()
    with col2:
        if st.button("Запустить", key="rerun"):
            st.session_state.turn = "assistant"
            st.rerun()

if prompt := st.chat_input("Твоя фраза"):
    st.session_state.messages.append(Message(role="user", content=prompt))
    st.session_state.turn = "assistant"
    st.rerun()


def build_context(session_state):
    return Context(
        situation=st.session_state.situation.description,
        player_role=st.session_state.situation.player_role,
        assistant_role=st.session_state.situation.assistant_role,
        assistant_role_description=st.session_state.situation.assistant_role_description,
        messages=[
            Message(
                role=message.role,
                content=message.content,
                explanation=message.explanation,
            )
            for message in session_state.messages
        ],
    )


if st.session_state.turn == "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Печатает..."):
            print(st.session_state.messages)
            context = build_context(st.session_state)
            response = get_response(context, session_id=st.session_state.session_id)
            # time.sleep(1)
            # response = "LOL"
        # st.write(response)
    st.session_state.messages.append(
        Message(
            role="assistant",
            content=response["aggression_plan"]["phrase"],
            explanation=json.dumps(response, indent=2, ensure_ascii=False),
        )
    )
    st.session_state.turn = "user"
    st.rerun()

last_message = st.session_state.messages[-1]
if (
    last_message.role == "assistant"
    and last_message.explanation
    and json.loads(last_message.explanation)["aggression_plan"]["tactic"]
    != "Manipulation"
):
    with st.chat_message("assistant", avatar="😎"):
        with st.spinner("Печатает..."):
            context = build_context(st.session_state)
            response = get_feedback(context, session_id=st.session_state.session_id)
    st.session_state.messages.append(Message(role="assistant", content=response))

    st.rerun()
