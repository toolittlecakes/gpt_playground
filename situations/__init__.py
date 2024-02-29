from .situation import Situation, Message
from .weekend_email import situation as weekend_email
from .mother_car import situation as mother_car

situations: dict[str, Situation] = {
    "weekend_email": weekend_email,
    "mother_car": mother_car,
}

DEFAULT_SITUATION = "mother_car"
