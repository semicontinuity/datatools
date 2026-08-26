from dataclasses import dataclass


@dataclass(kw_only=True)
class ClickhouseConnectionSettings:
    hostname: str
    port: int
    secure: bool
    database: str
    user: str
    password: str
