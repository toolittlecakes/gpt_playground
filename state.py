from enum import StrEnum


class State(StrEnum):
    intro = "intro"
    user_input = "user_input"
    response_generation = "response_generation"
    game_end = "game_end"
    feedback_generation = "feedback_generation"
    feedback_provided = "feedback_provided"
