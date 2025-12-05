import click
import json
from typing import Optional

from datatools.tg.db.config.database import DatabaseConfig
from datatools.tg.db.database_connection import DatabaseConnection
from datatools.tg.db.repository.message_repository import MessageRepository
from datatools.tg.db.repository.expanded_message_repository import ExpandedMessageRepository


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
@click.option(
    "--expand",
    is_flag=True,
    help="Include user information by joining with users table"
)
def messages_get(channel_id: Optional[int], limit: Optional[int], expand: bool):
    """Retrieve messages and output in JSON lines format."""
    try:
        # Get database configuration from environment
        config = DatabaseConfig.from_env()
        
        # Create database connection
        db = DatabaseConnection(config)
        
        if expand:
            # Use expanded message repository for user joins
            expanded_repo = ExpandedMessageRepository(db)
            messages = expanded_repo.get_all(channel_id=channel_id, limit=limit)
        else:
            # Use regular message repository
            message_repo = MessageRepository(db)
            messages = message_repo.get_all(channel_id=channel_id, limit=limit)
        
        # Output messages as JSON lines
        for message in messages:
            print(json.dumps(message.to_dict(), ensure_ascii=False))
        
    except Exception as e:
        click.echo(f"Error: Failed to retrieve messages: {e}", err=True)
        raise