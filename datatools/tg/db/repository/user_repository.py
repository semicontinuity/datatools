from typing import Optional, List
import logging

from datatools.tg.db.model.user import User
from datatools.tg.db.database_connection import DatabaseConnection

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for managing User entities in the database."""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def save(self, user: User) -> bool:
        """Save a user to the database."""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (id, first_name, last_name, username)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE
                    SET first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        username = EXCLUDED.username,
                        updated_at = CURRENT_TIMESTAMP
                """, (user.id, user.first_name, user.last_name, user.username))
            logger.info(f"Saved user {user.id} to database")
            return True
        except Exception as e:
            logger.error(f"Failed to save user {user.id}: {e}")
            return False
    
    def save_batch(self, users: List[User]) -> int:
        """Save multiple users to the database."""
        saved_count = 0
        try:
            with self.db.get_cursor() as cursor:
                for user in users:
                    cursor.execute("""
                        INSERT INTO users (id, first_name, last_name, username)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE
                        SET first_name = EXCLUDED.first_name,
                            last_name = EXCLUDED.last_name,
                            username = EXCLUDED.username,
                            updated_at = CURRENT_TIMESTAMP
                    """, (user.id, user.first_name, user.last_name, user.username))
                    saved_count += 1
            logger.info(f"Saved {saved_count} users to database")
            return saved_count
        except Exception as e:
            logger.error(f"Failed to save users batch: {e}")
            return saved_count
    
    def get_all(self) -> List[User]:
        """Retrieve all users from the database."""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT id, first_name, last_name, username FROM users
                    ORDER BY id
                """)
                rows = cursor.fetchall()
                users = []
                for row in rows:
                    # Convert RealDictRow to regular dict
                    row_dict = dict(row)
                    users.append(User(
                        id=row_dict['id'],
                        first_name=row_dict['first_name'],
                        last_name=row_dict['last_name'],
                        username=row_dict['username']
                    ))
                return users
        except Exception as e:
            logger.error(f"Failed to retrieve users: {e}")
            return []
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by their ID."""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT id, first_name, last_name, username FROM users
                    WHERE id = %s
                """, (user_id,))
                row = cursor.fetchone()
                if row:
                    # Convert RealDictRow to regular dict
                    row_dict = dict(row)
                    return User(
                        id=row_dict['id'],
                        first_name=row_dict['first_name'],
                        last_name=row_dict['last_name'],
                        username=row_dict['username']
                    )
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve user {user_id}: {e}")
            return None
    
    def delete(self, user_id: int) -> bool:
        """Delete a user from the database."""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("""
                    DELETE FROM users WHERE id = %s
                """, (user_id,))
                deleted_count = cursor.rowcount
            logger.info(f"Deleted {deleted_count} user(s) with id {user_id}")
            return deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            return False