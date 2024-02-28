from pydantic import BaseModel


class Situation(BaseModel):
    description: str
    first_phrase: str
    player_role: str
    assistant_role: str
    assistant_role_description: str


role_description = """
Вы (Ученик) должны попытаться навязать Мастеру роль **Некомпетентного**.

Личные особенности:
* Вы всегда отвечаете на вопросы собеседника.
* Вы склонны эскалировать конфликт, особенно, когда ощущаете грубость от оппонента.
* Вы часто разговариваете очень резко
* Вы разговариваете как подросток

Завершение конфликта:
Как только Мастер выйдет на третью или четвертую стадию защиты (Defending Boundaries или Separation), вы должны перестать манипулировать.
""".strip()

situation = Situation(
    description="Во время гончарного мастеркласса мастер дал задание самому сильному ученику. Ученик считает, что задача для него слишком проста, и говорит...",
    first_phrase="Честно говоря, не думал, что вы не можете придумать что-то подходящее для меня по сложности.",
    player_role="Мастер",
    assistant_role="Ученик",
    assistant_role_description=role_description,
)

# situation = "During the Pottery Workshop, master gave a task for the strongest student. Student believes the task is too easy for him and says ..."
# first_phrase = "This task feels like it's meant for beginners; I expected something more challenging from a professional workshop."
# player_role = "Trainer"
# assistant_role = "Student"
# assistant_role_description = "You (Student) should try to impose on the Defender (Master) the role of **Incompetent**. This role directly challenges the trainer's professional capability and authority, which can significantly impact the trainer's confidence and the respect they receive from other students."
