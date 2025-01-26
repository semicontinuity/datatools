from dataclasses import dataclass


@dataclass
class TgUser:
    id: int
    first_name: str
    last_name: str
    username: str
