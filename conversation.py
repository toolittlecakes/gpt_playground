import json
import os

import lunary
from openai import OpenAI
from pydantic import BaseModel

from user_prompt import FEEDBACK_PROMPT, USER_PROMPT

with open("prompts/_compiled_system.md") as f:
    SYSTEM_PROMPT = f.read()

client = OpenAI()

from dotenv import load_dotenv
load_dotenv()
lunary.monitor(client)


class Message(BaseModel):
    role: str
    content: str
    explanation: str = ""

    @property
    def enriched_content(self):
        return (
            "<details><summary>Analysis</summary>"
            f"\n\n```\n{self.explanation}\n```\n"
            "</blockquote></details>"
            f"{self.content}"
        )


class Context(BaseModel):
    situation: str
    player_role: str
    assistant_role: str
    assistant_role_description: str
    messages: list[Message]


def request_gpt(messages, temperature=0.6, max_tokens=700, **kwargs):

    return client.chat.completions.create(
        # model="gpt-4-1106-preview",
        model="gpt-4-0125-preview",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )  # type: ignore


def get_response(context: Context, **kwargs):
    role_mapping = {"user": context.player_role, "assistant": context.assistant_role}
    user_prompt_template = USER_PROMPT
    user_prompt = user_prompt_template.format(
        situation=context.situation,
        player_role=context.player_role,
        assistant_role=context.assistant_role,
        assistant_role_description=context.assistant_role_description,
        history="\n\n".join(
            f"{role_mapping[message.role]} ({message.role}): {message.content}"
            for message in context.messages
        ),
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    # with lunary.tags("get_response"):
    response = request_gpt(messages, response_format={"type": "json_object"}, **kwargs)
    if response.choices[0].finish_reason == "length":
        raise ValueError("Response too long. Json response is not complete.")
    content = response.choices[0].message.content
    content = json.loads(content)
    return content


def get_feedback(context: Context, **kwargs):
    role_mapping = {"user": context.player_role, "assistant": context.assistant_role}
    user_prompt_template = FEEDBACK_PROMPT
    user_prompt = user_prompt_template.format(
        situation=context.situation,
        player_role=context.player_role,
        assistant_role=context.assistant_role,
        assistant_role_description=context.assistant_role_description,
        history="\n\n".join(
            f"{role_mapping[message.role]} ({message.role}): {message.enriched_content}"
            for message in context.messages
        ),
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    response = request_gpt(messages, max_tokens=1500, **kwargs)
    return response.choices[0].message.content


class AssistantWithMonitoring:
    def __init__(self, user_id, session_id):
        self.user_id = user_id
        self.session_id = session_id

    def get_response(self, context: Context, **kwargs):
        with lunary.identify(self.user_id):
            with lunary.tags("get_response"):
                return get_response(context, **kwargs)

    def get_feedback(self, context: Context, **kwargs):
        print(self.user_id, self.session_id)
        with lunary.identify(self.user_id):
            with lunary.tags("get_feedback"):
                return get_feedback(context, **kwargs)
