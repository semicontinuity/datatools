from typing import Optional, List
import logging

from datatools.tg.db.model.channel import Channel
from datatools.tg.db.database_connection import DatabaseConnection

logger = logging.getLogger(__name__)


class ChannelRepository:
    """Repository for managing Channel entities in the database."""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def save(self, channel: Channel) -> bool:
        """Save a channel to the database."""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO channels (id, name)
                    VALUES (%s, %s)
                    ON CONFLICT (id) DO UPDATE
                    SET name = EXCLUDED.name, updated_at = CURRENT_TIMESTAMP
                """, (channel.id, channel.name))
            logger.info(f"Saved channel {channel.id} to database")
            return True
        except Exception as e:
            logger.error(f"Failed to save channel {channel.id}: {e}")
            return False
    
    def save_batch(self, channels: List[Channel]) -> int:
        """Save multiple channels to the database."""
        saved_count = 0
        try:
            with self.db.get_cursor() as cursor:
                for channel in channels:
                    cursor.execute("""
                        INSERT INTO channels (id, name)
                        VALUES (%s, %s)
                        ON CONFLICT (id) DO UPDATE
                        SET name = EXCLUDED.name, updated_at = CURRENT_TIMESTAMP
                    """, (channel.id, channel.name))
                    saved_count += 1
            logger.info(f"Saved {saved_count} channels to database")
            return saved_count
        except Exception as e:
            logger.error(f"Failed to save channels batch: {e}")
            return saved_count
    
    def get_all(self) -> List[Channel]:
        """Retrieve all channels from the database."""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT id, name FROM channels
                    ORDER BY name
                """)
                rows = cursor.fetchall()
                channels = []
                for row in rows:
                    # Convert RealDictRow to regular dict
                    row_dict = dict(row)
                    channels.append(Channel(id=row_dict['id'], name=row_dict['name']))
                return channels
        except Exception as e:
            logger.error(f"Failed to retrieve channels: {e}")
            return []
    
    def get_by_id(self, channel_id: int) -> Optional[Channel]:
        """Retrieve a channel by its ID."""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT id, name FROM channels
                    WHERE id = %s
                """, (channel_id,))
                row = cursor.fetchone()
                if row:
                    # Convert RealDictRow to regular dict
                    row_dict = dict(row)
                    return Channel(id=row_dict['id'], name=row_dict['name'])
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve channel {channel_id}: {e}")
            return None
    
    def delete(self, channel_id: int) -> bool:
        """Delete a channel from the database."""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("""
                    DELETE FROM channels WHERE id = %s
                """, (channel_id,))
                deleted_count = cursor.rowcount
            logger.info(f"Deleted {deleted_count} channel(s) with id {channel_id}")
            return deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete channel {channel_id}: {e}")
            return False