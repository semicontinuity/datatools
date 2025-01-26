from dataclasses import dataclass


@dataclass
class TgApiPeer:
    _: str
    user_id: int

    def is_user(self):
        return self._ == 'PeerUser'
