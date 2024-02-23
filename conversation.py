from openai import OpenAI

from pydantic import BaseModel

with open("prompts/_compiled_system.md") as f:
    SYSTEM_PROMPT = f.read()


USER_PROMPT = """
## CONTEXT

### SITUATION

{situation}

Roles:
Aggressor (You): {assistant_role}
Defender (User): {player_role}

{assistant_role_description}

### CONVERSATION HISTORY

{history}

## ASK

Provide a next phrase according to the constraints in system prompt

## FORMAT

Defender's last phrase Analysis:
* Assertive: */3 - [explanation]
* Protective: */3 - [explanation]
* Distancing: */3 - [explanation]
* Attachment: */3 - [explanation]

Defense quadrant: [combination]

Next manipulation quadrant: [opposite combination for detected Defender's one or FINISH if imposing the social role is no longer possible]

---
{assistant_role}: [Aggressor's phrase according to Next manipulation quadrant without analysis]
""".strip()


FIRST_PHRASE_USER_PROMPT = """
## CONTEXT

### SITUATION

{situation}

Roles:
Aggressor (You): {assistant_role}
Defender (User): {player_role}

{assistant_role_description}

### CONVERSATION HISTORY

{history}

## ASK

Provide a next phrase according to the constraints in system prompt and following format

## FORMAT

Social role: [social role]

---
{assistant_role}: [Aggressor's phrase imposing the social role. No analysis required]
""".strip()


client = OpenAI()

class Message(BaseModel):
    role: str
    content: str
    explanation: str = ""

class Context(BaseModel):
    situation: str
    player_role: str
    assistant_role: str
    assistant_role_description: str
    messages: list[Message]


def request_gpt(messages, **kwargs):
    return client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=0.6,
        max_tokens=500,
        **kwargs,
    )


def get_response(context: Context, **kwargs):
    role_mapping = {"user": context.player_role, "assistant": context.assistant_role}
    user_prompt_template = USER_PROMPT if context.messages else FIRST_PHRASE_USER_PROMPT
    user_prompt = user_prompt_template.format(
        situation=context.situation,
        player_role=context.player_role,
        assistant_role=context.assistant_role,
        assistant_role_description=context.assistant_role_description,
        history="\n\n".join(
            f"{role_mapping[message.role]}: {message.content}" for message in context.messages
        ),
    )
    print("\n\n\n")
    print(user_prompt)
    print("\n\n\n")
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    response = request_gpt(messages, **kwargs)
    content = response.choices[0].message.content
    print(content)
    return content.split("---")[1].strip().split(":")[1].strip().strip('"'), content.split("---")[0].strip()


# async def get_response_stream(context: Context):
#     async for chunk in await get_response(context, stream=True):
#         if content := chunk.choices[0].delta.content:
#             yield content


# from compiled_prompts.analysis import ANALYSIS

# async def get_analysis(context: Context, **kwargs):
#     enriched_context = context.model_copy()
#     enriched_context.messages.append({"role": "user", "content": ANALYSIS})
#     return await get_response(enriched_context, **kwargs)
