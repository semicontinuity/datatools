import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    """Represents a Telegram message."""
    id: int
    channel_id: Optional[int]
    user_id: Optional[int]
    content: Optional[str]
    message_date: datetime
    reply_to_msg_id: Optional[int]
    reply_to_top_id: Optional[int]
    is_forum_topic: bool
    message_type: str  # "Message" or "MessageService"
    raw_data: str  # Store the complete JSON for complex fields
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """Create a Message instance from a dictionary (JSON from messagez.py)."""
        
        # Extract basic fields
        message_id = data['id']
        message_type = data.get('_', 'Message')
        
        # Extract channel_id from peer_id
        peer_id = data.get('peer_id', {})
        channel_id = peer_id.get('channel_id') if peer_id.get('_') == 'PeerChannel' else None
        
        # Extract user_id from from_id
        from_id = data.get('from_id', {})
        user_id = from_id.get('user_id') if from_id and from_id.get('_') == 'PeerUser' else None
        
        # Extract message content
        content = data.get('message', '')
        if not content and message_type == 'MessageService':
            # For service messages, create a readable description
            action = data.get('action', {})
            action_type = action.get('_', 'Unknown')
            content = f"[Service: {action_type}]"
        
        # Parse date
        date_str = data.get('date', '')
        if isinstance(date_str, str):
            # Handle different date formats
            try:
                if '+' in date_str:
                    message_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    message_date = datetime.fromisoformat(date_str)
            except ValueError:
                message_date = datetime.now()
        else:
            message_date = datetime.now()
        
        # Extract reply information
        reply_to = data.get('reply_to', {})
        reply_to_msg_id = None
        reply_to_top_id = None
        is_forum_topic = False
        
        if reply_to:
            reply_to_msg_id = reply_to.get('reply_to_msg_id')
            reply_to_top_id = reply_to.get('reply_to_top_id')
            is_forum_topic = reply_to.get('forum_topic', False)
        
        # Store raw data as JSON string for complex fields
        raw_data = json.dumps(data, ensure_ascii=False)
        
        return cls(
            id=message_id,
            channel_id=channel_id,
            user_id=user_id,
            content=content,
            message_date=message_date,
            reply_to_msg_id=reply_to_msg_id,
            reply_to_top_id=reply_to_top_id,
            is_forum_topic=is_forum_topic,
            message_type=message_type,
            raw_data=raw_data
        )
    
    def to_dict(self) -> dict:
        """Convert the Message instance to a dictionary."""
        return {
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