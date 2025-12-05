import click
import json
from typing import Optional

from datatools.tg.db.config.database import DatabaseConfig
from datatools.tg.db.database_connection import DatabaseConnection
from datatools.tg.db.repository.message_repository import MessageRepository


@click.command()
@click.option(
    "--channel-id",
    type=int,
    help="Filter messages by channel ID"
)
@click.option(
    "--limit",
    type=int,
    help="Limit number of messages returned"
)
def messages_get(channel_id: Optional[int], limit: Optional[int]):
    """Retrieve messages and output in JSON lines format."""
    try:
        # Get database configuration from environment
        config = DatabaseConfig.from_env()
        
        # Create database connection
        db = DatabaseConnection(config)
        
        # Create message repository
        message_repo = MessageRepository(db)
        
        # Get messages from database
        messages = message_repo.get_all(channel_id=channel_id, limit=limit)
        
        # Output messages as JSON lines
        for message in messages:
            print(json.dumps(message.to_dict(), ensure_ascii=False))
        
    except Exception as e:
        click.echo(f"Error: Failed to retrieve messages: {e}", err=True)
        raise