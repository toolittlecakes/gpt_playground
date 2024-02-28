import json
import os
import uuid
from datetime import datetime, timedelta

import extra_streamlit_components as stx
import streamlit as st
from streamlit_extras.stylable_container import stylable_container

from conversation import AssistantWithMonitoring, Context, Message
from situation import situation
from dotenv import load_dotenv

load_dotenv()


# @st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()


cookie_manager = get_manager()

authenticated = cookie_manager.get("authenticated")
if not authenticated:
    password = st.text_input("Пароль")
    if password == os.getenv("PASSWORD"):
        authenticated = True
        cookie_manager.set("authenticated", authenticated)
    st.stop()



if cookie_manager.get("user_id") is None:
    cookie_manager.set(
        "user_id",
        str(uuid.uuid4()),
        expires_at=datetime.now() + timedelta(days=90),
    )

if "user_id" not in st.session_state:
    st.session_state.user_id = cookie_manager.get("user_id")

if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4()

if "situation" not in st.session_state:
    st.session_state.situation = situation.model_copy()


# @st.cache_resource
def get_assistant():
    return AssistantWithMonitoring(
        user_id=st.session_state.user_id, session_id=st.session_state.session_id
    )


assistant = get_assistant()

st.write("# Симулятор Конфликтов")
st.write("## Введение")

intro = """
Привет! Я верю, что лучшее обучение - на практике, когда ты можешь сначала самостоятельно решить задачу, совершить ошибки, а потом пытаться их исправить. К сожалению, в реальной жизни не очень много возможностей поэкпериментировать, и когда происходят конфликты, нет времени задуматься о своих действиях (ага, а потом в два часа ночи лежишь и думаешь, как надо было ответить).

Поэтому я сделал для тебя этот симулятор, где ты можешь попрактиковаться в разрешении конфликтов без явного риска для отношений с людьми. Все, что ты скажешь, останется здесь, и никто не узнает, что ты тут был (если ты не расскажешь 🤫).

Чтобы начать диалог - жми `Начать` и отвечай на фразы своего собеседника, который начинает конфликт. В конце он выдаст тебе фидбэк. Чтобы перезапустить ситуацию - обнови страницу 🔄.

P.s. Еще я оставил тебе возможности разработчика - ты можешь отредактировать ситуацию, смотреть скрытые "мысли" ассистента, а также отменять последние сообщения и перезапускать генерацию ответа. Но помни, что в реальной жизни у тебя не будет такой возможности 😉"
""".strip()
st.write(intro)

st.write("## Ситуация")
if st.toggle("Редактирование ситуации (не смотри, если хочешь играть по честному)"):
    st.session_state.situation.description = st.text_area(
        "Описание ситуации", value=st.session_state.situation.description
    )
    st.session_state.situation.player_role = st.text_input(
        "Роль игрока", value=st.session_state.situation.player_role
    )
    st.session_state.situation.assistant_role = st.text_input(
        "Роль ассистента", value=st.session_state.situation.assistant_role
    )
    st.session_state.situation.assistant_role_description = st.text_area(
        "Инструкция ассистента",
        value=st.session_state.situation.assistant_role_description,
    )
    st.session_state.situation.first_phrase = st.text_area(
        "Первая фраза ассистента", value=st.session_state.situation.first_phrase
    )
    # st.write(st.session_state.session_id)
    st.write(
        {"user_id": st.session_state.user_id, "session_id": st.session_state.session_id}
    )
st.write(st.session_state.situation.description)

if not st.button("Начать") and "messages" not in st.session_state:
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = [
        Message(role="assistant", content=st.session_state.situation.first_phrase)
    ]

if "turn" not in st.session_state:
    st.session_state.turn = (
        "user" if st.session_state.messages[-1].role == "assistant" else "assistant"
    )


# print(st.session_state.messages)
role_mapping = {
    "user": st.session_state.situation.player_role,
    "assistant": st.session_state.situation.assistant_role,
}

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
                    "<details><summary>Analysis</summary>"
                    f"\n\n```\n{message.explanation}\n```\n"
                    "</blockquote></details>",
                    unsafe_allow_html=True,
                )
                # st.write(message.enriched_content, unsafe_allow_html=True)
            # continue
        st.write(f"**{role_mapping[message.role]}**: {message.content}")

with st.container():
    col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
    with col1:
        if st.button("Удалить", key="delete_last_message", use_container_width=True):
            st.session_state.messages.pop()
            st.session_state.turn = "user"
            st.rerun()
    with col2:
        if st.button("Запустить", key="rerun", use_container_width=True):
            st.session_state.turn = "assistant"
            st.rerun()

    if st.session_state.turn == "feedback":
        with col3:
            if st.button("Получить фидбэк", key="feedback", use_container_width=True):
                st.session_state.turn = "feedback_request"
                st.rerun()

if prompt := st.chat_input(
    "Твой ответ", disabled=st.session_state.turn not in ["assistant", "user"]
):
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
            response = assistant.get_response(context)
    st.session_state.messages.append(
        Message(
            role="assistant",
            content=response["aggression_plan"]["phrase"],
            explanation=json.dumps(response, indent=2, ensure_ascii=False),
        )
    )
    st.session_state.turn = "user"
    st.rerun()


defence_analisys = [
    json.loads(m.explanation)["defence_analysis"]
    for m in st.session_state.messages
    if m.explanation
]
defence_score = (
    sum(int(analysis["score"]) for analysis in defence_analisys) / len(defence_analisys)
    if defence_analisys
    else 0
)

if st.session_state.turn == "user" and (
    (
        st.session_state.messages
        and st.session_state.messages[-1].explanation
        and json.loads(st.session_state.messages[-1].explanation)["aggression_plan"][
            "tactic"
        ]
        != "Manipulation"
    )
    or len(st.session_state.messages) > 20
    or (defence_score < 5 and len(st.session_state.messages) > 8)
):
    st.session_state.turn = "feedback"
    st.rerun()

if st.session_state.turn == "feedback_request":
    with st.chat_message("assistant", avatar="😎"):
        with st.spinner("Печатает..."):
            context = build_context(st.session_state)
            response = assistant.get_feedback(context)
    st.session_state.messages.append(Message(role="assistant", content=response))
    st.session_state.turn = "finish"
    st.rerun()
