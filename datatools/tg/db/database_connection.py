import logging
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor

from datatools.tg.db.config.database import DatabaseConfig

# Set up logging
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manage PostgreSQL database connections."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection = None
    
    def connect(self):
        """Establish a connection to the database."""
        try:
            self.connection = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password,
                database=self.config.database,
                cursor_factory=RealDictCursor
            )
            logger.info("Successfully connected to database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")
    
    @contextmanager
    def get_cursor(self):
        """Get a database cursor for executing queries."""
        if not self.connection:
            self.connect()
        
        if not self.connection:
            raise Exception("Failed to establish database connection")
        
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
    
    def execute_script(self, script_path: str):
        """Execute a SQL script file."""
        try:
            with open(script_path, 'r') as file:
                script = file.read()
            
            with self.get_cursor() as cursor:
                cursor.execute(script)
            
            logger.info(f"Successfully executed script: {script_path}")
        except Exception as e:
            logger.error(f"Failed to execute script {script_path}: {e}")
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    )
                """, (table_name,))
                result = cursor.fetchone()
                return result[0] if result else False
        except Exception as e:
            logger.error(f"Failed to check if table {table_name} exists: {e}")
            return False