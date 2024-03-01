import json
import os

import lunary
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from situations.situation import Situation
from user_prompt import FEEDBACK_PROMPT, USER_PROMPT

load_dotenv()

with open("prompts/_compiled_system.md") as f:
    SYSTEM_PROMPT = f.read()

client = OpenAI()

lunary.monitor(client)


def request_gpt(messages, temperature=0.6, max_tokens=700, **kwargs):
    return client.chat.completions.create(
        # model="gpt-4-1106-preview",
        model="gpt-4-0125-preview",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=60,
        **kwargs,
    )  # type: ignore


def get_response(situation: Situation, **kwargs):
    user_prompt_template = USER_PROMPT
    user_prompt = user_prompt_template.format(
        situation=situation.description,
        user_role=situation.user_role,
        assistant_role=situation.assistant_role,
        assistant_role_description=situation.assistant_role_description,
        history="\n\n".join(
            f"{message.role}: {message.content}" for message in situation.messages
        ),
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    response = request_gpt(messages, response_format={"type": "json_object"}, **kwargs)
    if response.choices[0].finish_reason == "length":
        raise ValueError("Response too long. Json response is not complete.")
    content = response.choices[0].message.content
    content = json.loads(content)
    return content


def get_feedback(situation: Situation, **kwargs):
    user_prompt_template = FEEDBACK_PROMPT
    user_prompt = user_prompt_template.format(
        situation=situation.description,
        user_role=situation.user_role,
        assistant_role=situation.assistant_role,
        assistant_role_description=situation.assistant_role_description,
        history="\n\n".join(
            # f"{message.role} ({message.role}): {message.enriched_content}"
            f"{message.role}: {message.content}"
            for message in situation.messages
        ),
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    response = request_gpt(messages, max_tokens=1500, timeout=120, **kwargs)
    return response.choices[0].message.content


class AssistantWithMonitoring:
    def __init__(self, user_id, session_id):
        self.user_id = user_id
        self.session_id = session_id

    def get_response(self, situation: Situation, **kwargs):
        with lunary.identify(self.user_id):
            with lunary.tags("get_response"):
                return get_response(situation, **kwargs)

    def get_feedback(self, situation: Situation, **kwargs):
        print(self.user_id, self.session_id)
        with lunary.identify(self.user_id):
            with lunary.tags("get_feedback"):
                return get_feedback(situation, **kwargs)
