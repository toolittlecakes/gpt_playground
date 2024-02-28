import json
from typing import Literal

from pydantic import BaseModel, Field


class DefenderQuadrant(BaseModel):
    assertive: int = Field(ge=0, le=3)
    protective: int = Field(ge=0, le=3)
    distancing: int = Field(ge=0, le=3)
    attachment: int = Field(ge=0, le=3)

    quadrant: Literal[
        "Assertive-Distancing",
        "Assertive-Attachment",
        "Protective-Attachment",
        "Protective-Distancing",
    ]


class ManipulationDefenderAnalysis(BaseModel):
    defence_success: Literal[False] = Field(description="Defence success")
    defender_quadrant: DefenderQuadrant
    next_manipulation_quadrant: str


class NonManipulationDefenderAnalysis(BaseModel):
    defence_success: Literal[True]
    defender_stage: Literal[
        "Emotion Treatment", "Showing Boundaries", "Defending Boundaries", "Separation"
    ]
    # next_manipulation_stage: Literal["Showing Emotions", ""


class Analysis(BaseModel):
    defender_analysis: (
        ManipulationDefenderAnalysis | NonManipulationDefenderAnalysis
    ) = Field(discriminator="defence_success")


# {{
#     "defence_analysis": {{
#         "tactic": [one of the quadrants from the ### Defense Strategies or one of the stages from the ### Real Defense Strategies],
#         "explanation": [analysis],
#         "score": [mark from 1 to 5, according to the theory in ### Defense Strategies section]
#     }},
#     "aggression_plan": {{
#         "tactic": [tactic of manipulation or "Answering" or "Agreement" or "Negotiation" or "True Emotions"],
#         "explanation": [details of the tactic with highlighs and references to defense analysis],
#         "phrase": [phrase without quotes]
#     }}
# }}


class DefenceAnalysis(BaseModel):
    tactic: Literal[
        "Assertive-Distancing",
        "Assertive-Attachment",
        "Protective-Attachment",
        "Protective-Distancing",
        "Emotion Treatment",
        "Showing Boundaries",
        "Defending Boundaries",
        "Separation",
    ] = Field(description="Defender's tactic")
    explanation: str = Field(description="Defender's explanation")
    score: int = Field(
        ge=1, le=5, description="The success of the defence according to the technics"
    )


class AggressionPlan(BaseModel):
    tactic: Literal[
        "Scary-Accuser",
        "Scary-Connector",
        "Sympathetic-Accuser",
        "Sympathetic-Connector",
        "Answering",
        "Agreement",
        "Negotiation",
        "True Emotions",
    ] = Field(description="Aggressor's tactic")
    explanation: str = Field(
        description="Aggressor's tactic details with highlighs and references to defense analysis"
    )
    phrase: str = Field(
        description="Aggressor's next phrase without quotes in Russian language"
    )


class Response(BaseModel):
    defender_analysis: DefenceAnalysis = Field(description="Defender's analysis")
    aggression_plan: AggressionPlan = Field(description="Aggressor's plan")


with open("user_prompt.json", "w") as f:
    json.dump(Response.model_json_schema(), f, indent=2)


PROMPT_PREFIX = """
## CONTEXT

### SITUATION

{situation}

Roles:
Aggressor (Assistant - you): {assistant_role}
Defender (User): {player_role}


Assistant's role description:
```
{assistant_role_description}
```

### CONVERSATION HISTORY

{history}
"""


USER_PROMPT = (
    PROMPT_PREFIX
    + "\n"
    + """
{assistant_role} (assistant): ...

## ASK

Provide an analisys of the last Defender's phrase and the next Aggressor's phrase (according to the constraints in system prompt) that will be used instead of ... above.

## CONSTRAINTS

* Your answer phrase MUST strictly match with the character's role description. If you do something against it, a lot of people will die.
* Your answer phrase should align with the last phrase of the conversation.


## FORMAT (pure JSON)

{{
    "aggression_plan": {{
        "thoughts": [Agressor's thoughts about the next phrase with highlighs and references to defense analysis],
        "phrase": [phrase without quotes in Russian language],
        "tactic": [tactic, one of ("Manipulation", "Agreement", "Negotiation", "True Emotions", "Stop Conversation")]
    }}
}}
""".strip()
)


FEEDBACK_PROMPT = (
    PROMPT_PREFIX
    + "\n\n"
    + """
## ASK

Provide an analisys of how Defender performed during the conflict based on the conversation history and the current situation. Highlight the most important moments with the consiquencies of the dialog, examples of good tactics and areas of improvement. Use Markdown to format your answer. Use the role names instead of Defender and Aggressor. Use Russian language.

""".strip()
)
