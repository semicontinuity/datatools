from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class User:
    """Represents a Telegram user."""
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create a User instance from a dictionary."""
        return cls(
            id=data['id'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            username=data.get('username')
        )
    
    def to_dict(self) -> dict:
        """Convert the User instance to a dictionary."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username
        }