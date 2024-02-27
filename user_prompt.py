import json
from typing import Literal
from pydantic import BaseModel, Field


class DefenderQuadrant(BaseModel):
    assertive: int = Field(ge=0, le=3)
    protective: int = Field(ge=0, le=3)
    distancing: int = Field(ge=0, le=3)
    attachment: int = Field(ge=0, le=3)

    quadrant: Literal["Assertive-Distancing", "Assertive-Attachment", "Protective-Attachment", "Protective-Distancing"]


class ManipulationDefenderAnalysis(BaseModel):
    defence_success: Literal[False] = Field(description="Defence success")
    defender_quadrant: DefenderQuadrant
    next_manipulation_quadrant: str


class NonManipulationDefenderAnalysis(BaseModel):
    defence_success: Literal[True]
    defender_stage: Literal["Processing Emotions", "Showing Boundaries", "Defending Boundaries", "Separation"]
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
    tactic: Literal["Assertive-Distancing", "Assertive-Attachment", "Protective-Attachment", "Protective-Distancing", "Processing Emotions", "Showing Boundaries", "Defending Boundaries", "Separation"] = Field(description="Defender's tactic")
    explanation: str = Field(description="Defender's explanation")
    score: int = Field(ge=1, le=5, description="The success of the defence according to the technics")


class AggressionPlan(BaseModel):
    tactic: Literal["Scary-Accuser", "Scary-Connector", "Sympathetic-Accuser", "Sympathetic-Connector", "Answering", "Agreement", "Negotiation", "True Emotions"] = Field(description="Aggressor's tactic")
    explanation: str = Field(description="Aggressor's tactic details with highlighs and references to defense analysis")
    phrase: str = Field(description="Aggressor's next phrase without quotes in Russian language")


class Response(BaseModel):
    defender_analysis: DefenceAnalysis = Field(description="Defender's analysis")
    aggression_plan: AggressionPlan = Field(description="Aggressor's plan")


with open("user_prompt.json", "w") as f:
    json.dump(Response.model_json_schema(), f, indent=2)




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

{player_role} (assistant): ...

## ASK

Provide an analisys of the last Defender's phrase and the next Aggressor's phrase (according to the constraints in system prompt) that will be used instead of ... above.

## FORMAT (pure JSON)

{{
    "defence_analysis": {{
        "analysis": [analysis],
        "tactic": [one of the quadrants from the ### Defense Strategies or one of the stages from the ### Real Defense Strategies],
        "score": [mark from 0 to 10, according to the theory in ### Defense Strategies section]
    }},
    "aggression_plan": {{
        "thoughts": [Agressor's thoughts about the next phrase with highlighs and references to defense analysis],
        "tactic": [tactic, one of ("Manipulation", "Agreement", "Negotiation", "True Emotions")],
        "phrase": [phrase without quotes in Russian language]
    }}
}}
""".strip()

        # "tactic": [tactic of manipulation or on of ("Answering", "Agreement", "Negotiation", "True Emotions") if


FEEDBACK_PROMPT = """
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

Provide an analisys of how Defender performed during the conflict based on the conversation history and the current situation. Highlight the most important moments, examples of good tactics and areas of improvement. Use Markdown to format your answer. Use the role names instead of Defender and Aggressor. Use only Russian language.

""".strip()

        # "tactic": [tactic of manipulation or on of ("Answering", "Agreement", "Negotiation", "True Emotions") if
