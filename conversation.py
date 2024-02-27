import json

import lunary
from openai import OpenAI
from pydantic import BaseModel

import env
from user_prompt import FEEDBACK_PROMPT, USER_PROMPT, Response

with open("prompts/_compiled_system.md") as f:
    SYSTEM_PROMPT = f.read()



client = OpenAI()
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
    print("\n\n\n")
    print(user_prompt)
    print("\n\n\n")
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    with lunary.tags("get_response"):
        response = request_gpt(messages, response_format={"type": "json_object"}, **kwargs)
    # phrase = ["aggression_plan"]["phrase"]
    if response.choices[0].finish_reason == "length":
        raise ValueError("Response too long. Json response is not complete.")
    content = response.choices[0].message.content
    print(content)
    content = json.loads(content)
    return content
    return phrase, response.model_dump_json()


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
    with lunary.tags("get_feedback"):
        response = request_gpt(messages, response_format={"type": "json_object"}, **kwargs)
    return response.choices[0].message.content


# async def get_response_stream(context: Context):
#     async for chunk in await get_response(context, stream=True):
#         if content := chunk.choices[0].delta.content:
#             yield content


# from compiled_prompts.analysis import ANALYSIS

# async def get_analysis(context: Context, **kwargs):
#     enriched_context = context.model_copy()
#     enriched_context.messages.append({"role": "user", "content": ANALYSIS})
#     return await get_response(enriched_context, **kwargs)
