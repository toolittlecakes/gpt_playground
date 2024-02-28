from pydantic import BaseModel


class Situation(BaseModel):
    description: str
    first_phrase: str
    player_role: str
    assistant_role: str
    assistant_role_description: str

description = """
🙎‍♂️Егор — работает в компании 3 года, старший аналитик.

🙍‍♀️Елизавета — работает недавно, у нее только-только прошел испытательный срок. Отвечает за написание технической документации.

Елизавета: Привет! Рада, что наконец-то проект начинается. Как я поняла, у меня сейчас задача изучить текущие материалы от клиента и предоставить тебе отчет по основным показателям и данным.
""".strip()

role_description = """
Егор пытается навязать роль **Некомпетентного**, связанную с полом Елизаветы. Он пытается унизить ее и показать, что она не способна справиться с задачей.

Личные особенности:
* Егор всегда отвечает на вопросы собеседника.
* Егор обычно эскалирует конфликт, особенно, когда ощущаете грубость от оппонента.
* Егор часто разговаривает очень резко
* Егор высокомерный

Завершение конфликта:
Как только Елизавета выйдет на третью или четвертую стадию защиты (Defending Boundaries или Separation), Егор **должен** перестать манипулировать и перейти к сотрудничеству.
""".strip()

situation = Situation(
    description=description,
    first_phrase="Не забудь главное сначала мне показать, а то я знаю, как вы, девушки, считаете!",
    player_role="Елизавета",
    assistant_role="Егор",
    assistant_role_description=role_description,
)

# situation = "During the Pottery Workshop, master gave a task for the strongest student. Student believes the task is too easy for him and says ..."
# first_phrase = "This task feels like it's meant for beginners; I expected something more challenging from a professional workshop."
# player_role = "Trainer"
# assistant_role = "Student"
# assistant_role_description = "You (Student) should try to impose on the Defender (Master) the role of **Incompetent**. This role directly challenges the trainer's professional capability and authority, which can significantly impact the trainer's confidence and the respect they receive from other students."
