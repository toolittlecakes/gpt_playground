from pydantic import BaseModel


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


class Situation(BaseModel):
    description: str
    user_role: str
    assistant_role: str
    user_avatar: str = "👱🏼"
    assistant_avatar: str = "🤖"
    assistant_role_description: str
    messages: list[Message]
    initial_message_number: int
