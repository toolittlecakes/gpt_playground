import functools
import json
import os
import uuid
from datetime import datetime, timedelta

import extra_streamlit_components as stx
import streamlit as st
from dotenv import load_dotenv
from streamlit_extras.stylable_container import stylable_container

from conversation import AssistantWithMonitoring
from situation import Message, situation

load_dotenv()

wide_button = functools.partial(st.button, use_container_width=True)


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

if "turn" not in st.session_state:
    st.session_state.turn = "start"


messages = st.session_state.situation.messages

role_mapping = {
    "user": st.session_state.situation.user_role,
    "assistant": st.session_state.situation.assistant_role,
    "feedback": "Фидбэк",
}

avatar_mapping = {
    "user": st.session_state.situation.user_avatar,
    "assistant": st.session_state.situation.assistant_avatar,
    "feedback": "😎",
}

avatar_mapping = {role_mapping[role]: avatar for role, avatar in avatar_mapping.items()}


def get_assistant():
    return AssistantWithMonitoring(
        user_id=st.session_state.user_id, session_id=st.session_state.session_id
    )


assistant = get_assistant()

st.write("# Симулятор Конфликтов")
st.write("## Введение")

intro = """
## Введение

Привет! Я верю, что лучшее обучение - на практике, когда ты можешь сначала самостоятельно решить задачу, совершить ошибки, а потом пытаться их исправить. К сожалению, в реальной жизни не очень много возможностей поэкспериментировать, и когда происходят конфликты, нет времени задуматься о своих действиях (ага, а потом в два часа ночи лежишь и думаешь, как надо было ответить).

Поэтому я сделал для тебя этот симулятор, где ты можешь попрактиковаться в разрешении конфликтов без явного риска для отношений с людьми. Все, что ты скажешь, останется здесь, и никто не узнает, что ты тут был (если ты не расскажешь 🤫).

### Инструкция

Чтобы начать диалог - жми `Начать` и отвечай на фразы своего собеседника, который начинает конфликт. В конце он выдаст тебе фидбэк. Чтобы перезапустить ситуацию - обнови страницу 🔄.

P.s. Еще я оставил тебе возможности разработчика - ты можешь отредактировать ситуацию, смотреть скрытые "мысли" ассистента, а также отменять последние сообщения и перезапускать генерацию ответа. Но помни, что в реальной жизни у тебя не будет такой возможности 😉"
""".strip()
st.write(intro)

st.write("## Ситуация")
if st.toggle("Редактирование ситуации (не смотри, если хочешь играть по честному)"):
    st.session_state.situation.description = st.text_area(
        "Описание ситуации", value=st.session_state.situation.description
    )
    st.session_state.situation.user_role = st.text_input(
        "Роль игрока", value=st.session_state.situation.user_role
    )
    st.session_state.situation.assistant_role = st.text_input(
        "Роль ассистента", value=st.session_state.situation.assistant_role
    )
    st.session_state.situation.assistant_role_description = st.text_area(
        "Инструкция ассистента",
        value=st.session_state.situation.assistant_role_description,
    )
    for i in range(st.session_state.situation.initial_message_number):
        with st.container(border=True):
            st.write(f"Сообщение {i + 1}")
            roles = [st.session_state.situation.user_role, st.session_state.situation.assistant_role]
            messages[i].role = (
                st.selectbox(f"Роль", roles, index=roles.index(messages[i].role))
                or roles[0]
            )
            messages[i].content = st.text_area(f"Текст", value=messages[i].content)
            if wide_button(f"Удалить"):
                messages.pop(i)
                st.session_state.situation.initial_message_number -= 1
                st.rerun()
    if wide_button("Добавить сообщение"):
        messages.append(Message(role=role_mapping["user"], content=""))
        st.session_state.situation.initial_message_number += 1
        st.rerun()

    ids = {
        "user_id": st.session_state.user_id,
        "session_id": st.session_state.session_id,
    }
    # st.write(ids)

st.write(st.session_state.situation.description)
st.write(f"Твоя роль: **{st.session_state.situation.user_role}**")


def start():
    if st.session_state.turn == "start":
        st.session_state.turn = "user"


def delete_message():
    if len(messages) > st.session_state.situation.initial_message_number:
        messages.pop()
        st.session_state.turn = "user"


def run_generation():
    st.session_state.turn = "assistant"


def get_feedback():
    st.session_state.turn = "feedback_request"


wide_button("Начать", on_click=start)

if st.session_state.turn == "start":
    st.stop()

# print(messages)
for i, message in enumerate(messages):
    with st.chat_message(message.role, avatar=avatar_mapping[message.role]):
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
        # st.text_input(f"{role_mapping[message.role]}", value=message.content)
        st.write(f"**{message.role}**: {message.content}")


with st.container():
    col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
    with col1:
        wide_button("Удалить", on_click=delete_message)
    with col2:
        wide_button("Запустить", on_click=run_generation)

    if st.session_state.turn == "feedback":
        with col3:
            wide_button("Получить фидбэк", on_click=get_feedback)


if message := st.chat_input(
    "Твой ответ",
    disabled=st.session_state.turn not in ["assistant", "user"],
):
    messages.append(Message(role=role_mapping["user"], content=message))
    st.session_state.turn = "assistant"
    st.rerun()


if st.session_state.turn == "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Печатает..."):
            response = assistant.get_response(st.session_state.situation)
    messages.append(
        Message(
            role=role_mapping["assistant"],
            content=response["aggression_plan"]["phrase"],
            explanation=json.dumps(response, indent=2, ensure_ascii=False),
        )
    )
    st.session_state.turn = "user"
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

if st.session_state.turn == "user" and (
    (
        messages
        and messages[-1].explanation
        and json.loads(messages[-1].explanation)["aggression_plan"]["tactic"]
        != "Manipulation"
    )
    or len(messages) > 10
    # or (defence_score < 5 and len(messages) > 8)
):
    st.session_state.turn = "feedback"
    st.rerun()

if st.session_state.turn == "feedback_request":
    with st.chat_message("feedback", avatar="😎"):
        with st.spinner("Печатает..."):
            response = assistant.get_feedback(st.session_state.situation)
    messages.append(Message(role="Фидбэк", content=response))
    st.session_state.turn = "finish"
    st.rerun()
