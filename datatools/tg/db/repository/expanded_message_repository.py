import logging
from typing import Optional, List

from datatools.tg.db.database_connection import DatabaseConnection
from datatools.tg.db.model.expanded_message import ExpandedMessage

logger = logging.getLogger(__name__)


class ExpandedMessageRepository:
    """Repository for managing ExpandedMessage entities with user joins."""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def get_all(self, channel_id: Optional[int] = None, limit: Optional[int] = None) -> List[ExpandedMessage]:
        """Retrieve messages with user information from the database."""
        try:
            with self.db.get_cursor() as cursor:
                query = """
                    SELECT m.id, m.channel_id, m.user_id, m.content, m.message_date,
                           m.reply_to_msg_id, m.reply_to_top_id, m.is_forum_topic,
                           u.first_name as user_first_name, u.last_name as user_last_name, u.username as user_username
                    FROM messages m
                    LEFT JOIN users u ON m.user_id = u.id
                """
                params = []
                
                if channel_id is not None:
                    query += " WHERE m.channel_id = %s"
                    params.append(channel_id)
                
                query += " ORDER BY m.message_date DESC"
                
                if limit is not None:
                    query += " LIMIT %s"
                    params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                messages = []
                for row in rows:
                    row_dict = dict(row)
                    # Add missing fields for ExpandedMessage.from_joined_data
                    row_dict['message_type'] = 'Message'  # Default type
                    row_dict['raw_data'] = '{}'  # Empty raw data
                    
                    expanded_message = ExpandedMessage.from_joined_data(row_dict)
                    messages.append(expanded_message)
                return messages
        except Exception as e:
            logger.error(f"Failed to retrieve expanded messages: {e}")
            return []
    
    def get_by_id(self, message_id: int) -> Optional[ExpandedMessage]:
        """Retrieve an expanded message by its ID."""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT m.id, m.channel_id, m.user_id, m.content, m.message_date,
                           m.reply_to_msg_id, m.reply_to_top_id, m.is_forum_topic,
                           u.first_name as user_first_name, u.last_name as user_last_name, u.username as user_username
                    FROM messages m
                    LEFT JOIN users u ON m.user_id = u.id
                    WHERE m.id = %s
                """, (message_id,))
                row = cursor.fetchone()
                if row:
                    row_dict = dict(row)
                    # Add missing fields for ExpandedMessage.from_joined_data
                    row_dict['message_type'] = 'Message'  # Default type
                    row_dict['raw_data'] = '{}'  # Empty raw data
                    
                    return ExpandedMessage.from_joined_data(row_dict)
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve expanded message {message_id}: {e}")
            return None