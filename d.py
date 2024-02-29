from enum import Enum


class State(Enum):
    intro = "intro"
    situation = "situation"
    conversation = "conversation"
    feedback = "feedback"
    outro = "outro"


x = {"state": State.intro}

x["state"] = State.situation
print(State.intro)
print(repr(State.intro))
print(type(State.intro))
print(type(State.intro.value))
print(x["state"] == State.situation)
