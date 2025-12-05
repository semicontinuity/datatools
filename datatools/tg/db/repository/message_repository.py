from typing import Optional, List
import logging

from datatools.tg.db.model.message import Message
from datatools.tg.db.database_connection import DatabaseConnection

logger = logging.getLogger(__name__)


class MessageRepository:
    """Repository for managing Message entities in the database."""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def save(self, message: Message) -> bool:
        """Save a message to the database."""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO messages (
                        id, channel_id, user_id, content, message_date,
                        reply_to_msg_id, reply_to_top_id, is_forum_topic
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE
                    SET 
                        channel_id = EXCLUDED.channel_id,
                        user_id = EXCLUDED.user_id,
                        content = EXCLUDED.content,
                        message_date = EXCLUDED.message_date,
                        reply_to_msg_id = EXCLUDED.reply_to_msg_id,
                        reply_to_top_id = EXCLUDED.reply_to_top_id,
                        is_forum_topic = EXCLUDED.is_forum_topic,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    message.id, message.channel_id, message.user_id, message.content,
                    message.message_date, message.reply_to_msg_id, message.reply_to_top_id,
                    message.is_forum_topic
                ))
            logger.info(f"Saved message {message.id} to database")
            return True
        except Exception as e:
            logger.error(f"Failed to save message {message.id}: {e}")
            return False
    
    def save_batch(self, messages: List[Message]) -> int:
        """Save multiple messages to the database."""
        saved_count = 0
        try:
            with self.db.get_cursor() as cursor:
                for message in messages:
                    cursor.execute("""
                        INSERT INTO messages (
                            id, channel_id, user_id, content, message_date,
                            reply_to_msg_id, reply_to_top_id, is_forum_topic
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE
                        SET 
                            channel_id = EXCLUDED.channel_id,
                            user_id = EXCLUDED.user_id,
                            content = EXCLUDED.content,
                            message_date = EXCLUDED.message_date,
                            reply_to_msg_id = EXCLUDED.reply_to_msg_id,
                            reply_to_top_id = EXCLUDED.reply_to_top_id,
                            is_forum_topic = EXCLUDED.is_forum_topic,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        message.id, message.channel_id, message.user_id, message.content,
                        message.message_date, message.reply_to_msg_id, message.reply_to_top_id,
                        message.is_forum_topic
                    ))
                    saved_count += 1
            logger.info(f"Saved {saved_count} messages to database")
            return saved_count
        except Exception as e:
            logger.error(f"Failed to save messages batch: {e}")
            return saved_count
    
    def get_all(self, channel_id: Optional[int] = None, limit: Optional[int] = None) -> List[Message]:
        """Retrieve messages from the database."""
        try:
            with self.db.get_cursor() as cursor:
                query = """
                    SELECT id, channel_id, user_id, content, message_date,
                           reply_to_msg_id, reply_to_top_id, is_forum_topic
                    FROM messages
                """
                params = []
                
                if channel_id is not None:
                    query += " WHERE channel_id = %s"
                    params.append(channel_id)
                
                query += " ORDER BY message_date DESC"
                
                if limit is not None:
                    query += " LIMIT %s"
                    params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                messages = []
                for row in rows:
                    row_dict = dict(row)
                    # Create a simplified message object for output
                    message = Message(
                        id=row_dict['id'],
                        channel_id=row_dict['channel_id'],
                        user_id=row_dict['user_id'],
                        content=row_dict['content'],
                        message_date=row_dict['message_date'],
                        reply_to_msg_id=row_dict['reply_to_msg_id'],
                        reply_to_top_id=row_dict['reply_to_top_id'],
                        is_forum_topic=row_dict['is_forum_topic'],
                        message_type='Message',  # Default type for output
                        raw_data='{}'  # Empty raw data for output
                    )
                    messages.append(message)
                return messages
        except Exception as e:
            logger.error(f"Failed to retrieve messages: {e}")
            return []
    
    def get_by_id(self, message_id: int) -> Optional[Message]:
        """Retrieve a message by its ID."""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT id, channel_id, user_id, content, message_date,
                           reply_to_msg_id, reply_to_top_id, is_forum_topic
                    FROM messages
                    WHERE id = %s
                """, (message_id,))
                row = cursor.fetchone()
                if row:
                    row_dict = dict(row)
                    return Message(
                        id=row_dict['id'],
                        channel_id=row_dict['channel_id'],
                        user_id=row_dict['user_id'],
                        content=row_dict['content'],
                        message_date=row_dict['message_date'],
                        reply_to_msg_id=row_dict['reply_to_msg_id'],
                        reply_to_top_id=row_dict['reply_to_top_id'],
                        is_forum_topic=row_dict['is_forum_topic'],
                        message_type='Message',
                        raw_data='{}'
                    )
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve message {message_id}: {e}")
            return None
    
    def delete(self, message_id: int) -> bool:
        """Delete a message from the database."""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("""
                    DELETE FROM messages WHERE id = %s
                """, (message_id,))
                deleted_count = cursor.rowcount
            logger.info(f"Deleted {deleted_count} message(s) with id {message_id}")
            return deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete message {message_id}: {e}")
            return False