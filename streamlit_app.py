import functools
import json
import os
import time
import uuid
from datetime import datetime, timedelta

import extra_streamlit_components as stx
import streamlit as st
from dotenv import load_dotenv
from streamlit_extras.stylable_container import stylable_container

from conversation import AssistantWithMonitoring
from situations import situations, Message, DEFAULT_SITUATION
from state import State

load_dotenv()

wide_button = functools.partial(st.button, use_container_width=True)


def get_manager():
    return stx.CookieManager()


cookie_manager = get_manager()

# if cookie_manager.get("authenticated"):
#     cookie_manager.delete("authenticated")

authenticated = cookie_manager.get("authenticated")
if not authenticated:
    password = st.text_input("Пароль")
    if password == os.getenv("PASSWORD"):
        authenticated = "user"
        cookie_manager.set("authenticated", authenticated)
    if password == os.getenv("ADMIN_PASSWORD"):
        authenticated = "admin"
        cookie_manager.set("authenticated", authenticated)
    st.stop()


if cookie_manager.get("user_id") is None:
    cookie_manager.set(
        "user_id",
        str(uuid.uuid4()),
        expires_at=datetime.now() + timedelta(days=90),
    )

ss = st.session_state

# if "authenticated" not in ss:
#     password = st.text_input("Пароль")
#     if password == os.getenv("PASSWORD"):
#         ss.authenticated = "user"
#         st.rerun()
#     if password == os.getenv("ADMIN_PASSWORD"):
#         ss.authenticated = "admin"
#         st.rerun()
#     st.stop()

if "current_situation" not in ss:
    ss.current_situation = DEFAULT_SITUATION
situation = situations[ss.current_situation]

if "user_id" not in ss:
    ss.user_id = cookie_manager.get("user_id")

if "session_id" not in ss:
    ss.session_id = uuid.uuid4()

if "situation" not in ss:
    ss.situation = situation.model_copy(deep=True)

if "state" not in ss:
    ss.state = State.intro

messages = ss.situation.messages
role_mapping = {
    "user": ss.situation.user_role,
    "assistant": ss.situation.assistant_role,
    "feedback": "Фидбэк",
}

avatar_mapping = {
    "user": ss.situation.user_avatar,
    "assistant": ss.situation.assistant_avatar,
    "feedback": "😎",
}

avatar_mapping = {role_mapping[role]: avatar for role, avatar in avatar_mapping.items()}


def get_assistant():
    return AssistantWithMonitoring(user_id=ss.user_id, session_id=ss.session_id)


assistant = get_assistant()

st.write("# Симулятор Конфликтов")

intro = """
## Введение

Привет! Это симулятор, где ты можешь попрактиковаться в разрешении конфликтов без явного риска для отношений с людьми в реальности. Все, что ты скажешь, останется здесь, и никто не узнает, что ты тут был (если ты не расскажешь 🤫).

### Инструкция

Чтобы начать диалог - жми `Начать` и отвечай на фразы своего собеседника, который начинает конфликт. В конце он выдаст тебе фидбэк. Чтобы перезапустить ситуацию - обнови страницу 🔄.

P.s. Еще я оставил тебе часть возможностей разработчика - ты можешь отредактировать ситуацию или даже поменять на свою, если хочешь.
""".strip()

st.write(intro)



st.write("## Ситуация")
if option := st.selectbox(
    "Выбор ситуации",
    list(situations.keys()),
    index=list(situations.keys()).index(ss.current_situation),
):
    if option != ss.current_situation:
        print("option", option, ss.current_situation)
        ss.situation = situations[option].model_copy(deep=True)
        ss.state = State.intro
        ss.current_situation = option
        st.rerun()

if st.toggle("Редактирование ситуации (не смотри, если хочешь играть по честному)"):
    ss.situation.description = st.text_area(
        "Описание ситуации", value=ss.situation.description
    )
    ss.situation.user_role = st.text_input("Роль игрока", value=ss.situation.user_role)
    ss.situation.assistant_role = st.text_input(
        "Роль ассистента", value=ss.situation.assistant_role
    )
    ss.situation.assistant_role_description = st.text_area(
        "Инструкция ассистента",
        value=ss.situation.assistant_role_description,
    )
    for i in range(ss.situation.initial_message_number):
        with st.container(border=True):
            st.write(f"Сообщение {i + 1}")
            roles = [
                ss.situation.user_role,
                ss.situation.assistant_role,
            ]
            messages[i].role = (
                st.selectbox(
                    f"Роль",
                    roles,
                    index=roles.index(messages[i].role),
                    key=f"role_default_message_{i}",
                )
                or roles[0]
            )
            messages[i].content = st.text_area(f"Текст", value=messages[i].content)
            if wide_button(f"Удалить", key=f"delete_default_message_{i}"):
                messages.pop(i)
                ss.situation.initial_message_number -= 1
                st.rerun()
    if wide_button("Добавить сообщение"):
        messages.append(Message(role=ss.situation.user_role, content=""))
        ss.situation.initial_message_number += 1
        st.rerun()

    ids = {
        "user_id": ss.user_id,
        "session_id": ss.session_id,
    }

st.write(ss.situation.description)
st.write(f"Твоя роль: **{ss.situation.user_role}**")


def start():
    if ss.state == State.intro:
        ss.state = State.user_input


def delete_message():
    if len(messages) > ss.situation.initial_message_number:
        messages.pop()
        ss.state = State.user_input


def run_generation():
    ss.state = State.response_generation


def get_feedback():
    ss.state = State.feedback_generation


wide_button("Начать", on_click=start)

if ss.state == State.intro:
    st.stop()


for i, message in enumerate(messages):
    with st.chat_message(message.role, avatar=avatar_mapping[message.role]):
        if message.explanation and authenticated == "admin":
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
        # st.text_input(f"{role_mapping[message.role]}", value=message.content)
        st.write(f"**{message.role}**: {message.content}")


if authenticated == "admin":
    with st.container():
        col1, col2, col3 = st.columns([0.25, 0.25, 0.5])
        with col1:
            wide_button(
                "Удалить",
                on_click=delete_message,
                disabled=len(messages) <= ss.situation.initial_message_number,
            )
        with col2:
            wide_button(
                "Запустить",
                on_click=run_generation,
                disabled=ss.state != State.user_input,
            )

        with col3:
            wide_button(
                "Получить фидбэк",
                on_click=get_feedback,
                disabled=ss.state not in [State.game_end, State.user_input],
            )
else:
    if ss.state == State.game_end:
        wide_button(
            "Получить фидбэк",
            on_click=get_feedback,
            disabled=ss.state != State.game_end,
        )


if message := st.chat_input(
    "Твой ответ",
    disabled=ss.state not in [State.user_input, State.response_generation],
):
    messages.append(Message(role=ss.situation.user_role, content=message))
    ss.state = State.response_generation
    st.rerun()


if ss.state == State.response_generation:
    with st.chat_message(
        ss.situation.assistant_role, avatar=avatar_mapping[ss.situation.assistant_role]
    ):
        with st.spinner("Печатает..."):
            response = assistant.get_response(ss.situation)

    messages.append(
        Message(
            role=ss.situation.assistant_role,
            content=response["phrase"],
            explanation=json.dumps(response, indent=2, ensure_ascii=False),
        )
    )
    ss.state = State.user_input
    st.rerun()


# defence_analisys = [
#     json.loads(m.explanation)["defence_analysis"]
#     for m in messages
#     if m.explanation
# ]
# defence_score = (
#     sum(int(analysis["score"]) for analysis in defence_analisys) / len(defence_analisys)
#     if defence_analisys
#     else 0
# )
if messages and messages[-1].explanation:
    print(json.loads(messages[-1].explanation)["next_behaviour_type"])
if ss.state == State.user_input and (
    (
        messages
        and messages[-1].explanation
        and json.loads(messages[-1].explanation)["next_behaviour_type"] != "Manipulation"
    )
    or len(messages) > 10
    # or (defence_score < 5 and len(messages) > 8)
):
    ss.state = State.game_end
    st.rerun()

if ss.state == State.feedback_generation:
    with st.chat_message("Фидбэк", avatar="😎"):
        with st.spinner("Печатает..."):
            response = assistant.get_feedback(ss.situation)
    messages.append(Message(role="Фидбэк", content=response))
    ss.state = State.feedback_provided
    st.rerun()
