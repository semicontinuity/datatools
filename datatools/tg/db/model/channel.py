from dataclasses import dataclass
from typing import Optional, List
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class Channel:
    """Represents a Telegram channel."""
    id: int
    name: str
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Channel':
        """Create a Channel instance from a dictionary."""
        return cls(
            id=data['id'],
            name=data['name']
        )
    
    def to_dict(self) -> dict:
        """Convert the Channel instance to a dictionary."""
        return {
            'id': self.id,
            'name': self.name
        }