import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from datatools.tg.db.model.message import Message
from datatools.tg.db.model.user import User


@dataclass
class ExpandedMessage:
    """Represents a Telegram message with expanded user information."""
    id: int
    channel_id: Optional[int]
    user_id: Optional[int]
    content: Optional[str]
    message_date: datetime
    reply_to_msg_id: Optional[int]
    reply_to_top_id: Optional[int]
    is_forum_topic: bool
    message_type: str
    raw_data: str
    # Expanded user information
    user_first_name: Optional[str] = None
    user_last_name: Optional[str] = None
    user_username: Optional[str] = None
    
    @classmethod
    def from_message_and_user(cls, message: Message, user: Optional[User] = None) -> 'ExpandedMessage':
        """Create an ExpandedMessage from a Message and optional User."""
        return cls(
            id=message.id,
            channel_id=message.channel_id,
            user_id=message.user_id,
            content=message.content,
            message_date=message.message_date,
            reply_to_msg_id=message.reply_to_msg_id,
            reply_to_top_id=message.reply_to_top_id,
            is_forum_topic=message.is_forum_topic,
            message_type=message.message_type,
            raw_data=message.raw_data,
            user_first_name=user.first_name if user else None,
            user_last_name=user.last_name if user else None,
            user_username=user.username if user else None
        )
    
    @classmethod
    def from_joined_data(cls, data: dict) -> 'ExpandedMessage':
        """Create an ExpandedMessage from joined database query result."""
        # Parse message_date if it's a string
        message_date = data['message_date']
        if isinstance(message_date, str):
            try:
                message_date = datetime.fromisoformat(message_date.replace('Z', '+00:00'))
            except ValueError:
                message_date = datetime.now()
        
        return cls(
            id=data['id'],
            channel_id=data['channel_id'],
            user_id=data['user_id'],
            content=data['content'],
            message_date=message_date,
            reply_to_msg_id=data['reply_to_msg_id'],
            reply_to_top_id=data['reply_to_top_id'],
            is_forum_topic=data['is_forum_topic'],
            message_type=data['message_type'],
            raw_data=data['raw_data'],
            user_first_name=data.get('user_first_name'),
            user_last_name=data.get('user_last_name'),
            user_username=data.get('user_username')
        )
    
    def to_dict(self) -> dict:
        """Convert the ExpandedMessage instance to a dictionary."""
        result = {
            'id': self.id,
            'channel_id': self.channel_id,
            'user_id': self.user_id,
            'content': self.content,
            'message_date': self.message_date.isoformat(),
            'reply_to_msg_id': self.reply_to_msg_id,
            'reply_to_top_id': self.reply_to_top_id,
            'is_forum_topic': self.is_forum_topic,
            'message_type': self.message_type,
            'raw_data': json.loads(self.raw_data) if self.raw_data else {}
        }
        
        # Add user information if available
        if self.user_first_name is not None or self.user_last_name is not None or self.user_username is not None:
            result['user'] = {
                'first_name': self.user_first_name,
                'last_name': self.user_last_name,
                'username': self.user_username
            }
        
        return result