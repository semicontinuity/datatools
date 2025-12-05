import click
import json
import sys

from datatools.tg.db.config.database import DatabaseConfig
from datatools.tg.db.database_connection import DatabaseConnection
from datatools.tg.db.model.message import Message
from datatools.tg.db.repository.message_repository import MessageRepository


@click.command()
def messages_put():
    """Import messages from STDIN in JSON lines format."""
    try:
        # Get database configuration from environment
        config = DatabaseConfig.from_env()
        
        # Create database connection
        db = DatabaseConnection(config)
        
        # Create message repository
        message_repo = MessageRepository(db)
        
        # Read JSON lines from STDIN
        messages = []
        for line in sys.stdin:
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                    message = Message.from_dict(data)
                    messages.append(message)
                except json.JSONDecodeError as e:
                    click.echo(f"Warning: Failed to parse JSON line: {e}", err=True)
                    continue
                except Exception as e:
                    click.echo(f"Warning: Failed to process message: {e}", err=True)
                    continue
        
        # Save messages to database
        saved_count = message_repo.save_batch(messages)
        
        click.echo(f"Successfully imported {saved_count} messages")
        
    except Exception as e:
        click.echo(f"Error: Failed to import messages: {e}", err=True)
        raise