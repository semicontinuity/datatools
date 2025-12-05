import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """Database configuration from environment variables."""
    
    host: str
    port: int
    username: str
    password: str
    database: str
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create database configuration from environment variables."""
        return cls(
            host=os.environ.get('DB_HOST', 'localhost'),
            port=int(os.environ.get('DB_PORT', 5432)),
            username=os.environ['DB_USERNAME'],
            password=os.environ['DB_PASSWORD'],
            database=os.environ.get('DB_DATABASE', 'telegram_db')
        )
    
    @property
    def connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
