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


description = """
Ничего не предвещало беды в понедельник утром, когда Коля открывал корпоративную почту перед еженедельным совещанием отдела.

Однако письмо с пометкой «Срочно! Новые KPI!» уже своим заголовком взбодрило больше чашки кофе, которую он так и не успели сварить.
""".strip()

role_description = """
Стас пытается навязать роль **Немотивированного** сотрудника. Он пытается унизить Колю и показать, что он не способен серьезно относиться к задаче.

Личные особенности:
* Стас всегда отвечает на вопросы собеседника.
* Стас обычно эскалирует конфликт, особенно, когда ощущаете грубость от оппонента.
* Стас часто подает манипуляцию под видом безобидной шутки или совета.
* Стас высокомерный

Завершение конфликта:
Как только Коля выйдет на третью или четвертую стадию защиты (Defending Boundaries или Separation), Стас **должен** перестать манипулировать и перейти к сотрудничеству.
""".strip()

situation = Situation(
    description=description,
    user_role="Коля",
    assistant_role="Стас",
    user_avatar="👱🏻‍♂️",
    assistant_avatar="🧔🏼‍♂️",
    assistant_role_description=role_description,
    messages=[
        Message(
            role="Коля",
            content="Какие еще новые KPI? Мы же согласовали их только неделю назад…",
        ),
        Message(
            role="Стас",
            content="Коля, привет! Отличная новость — у тебя есть возможность проявить себя и доказать, что мы не зря дали тебе возможность занять пост менеджера отдела. Головной офис пересмотрел KPI, которые мы им отправили. Успел прочитать вчера?",
        ),
        Message(
            role="Коля",
            content="Нет еще, вчера почту не проверял…",
        ),
        Message(
            role="Стас",
            content="Коля, сотрудники, которые хотят повышения, каждый час проверяют почту, включая выходные!",
        ),
    ],
    initial_message_number=4,
)
