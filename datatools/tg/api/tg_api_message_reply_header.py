from dataclasses import dataclass


@dataclass
class TgApiMessageReplyHeader:
    forum_topic: bool
    reply_to_msg_id: int = None
    reply_to_top_id: int = None
