from pydantic import BaseModel, Field


class DefenderQuadrant(BaseModel):
    assertive: float = Field(..., ge=0, le=3)
    protective: float = Field(..., ge=0, le=3)
    distancing: float = Field(..., ge=0, le=3)
    attachment: float = Field(..., ge=0, le=3)


class ManipulationDefenderAnalysis(BaseModel):
    defender_quadrant: DefenderQuadrant
    next_manipulation_quadrant: str
    defence_success: bool = False


class NonManipulationDefenderAnalysis(BaseModel):
    defender_quadrant: DefenderQuadrant
    next_manipulation_quadrant: str
    defence_success: bool = False


pr


USER_PROMPT = """
## CONTEXT

### SITUATION

{situation}

Roles:
Aggressor (You): {assistant_role}
Defender (User): {user_role}

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
Defender (User): {user_role}

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
