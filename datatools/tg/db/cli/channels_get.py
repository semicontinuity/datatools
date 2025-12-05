import click
import json

from datatools.tg.db.config.database import DatabaseConfig
from datatools.tg.db.database_connection import DatabaseConnection
from datatools.tg.db.repository.channel_repository import ChannelRepository


@click.command()
def channels_get():
    """Retrieve all channels and output in JSON lines format."""
    try:
        # Get database configuration from environment
        config = DatabaseConfig.from_env()
        
        # Create database connection
        db = DatabaseConnection(config)
        
        # Create channel repository
        channel_repo = ChannelRepository(db)
        
        # Get all channels from database
        channels = channel_repo.get_all()
        
        # Output channels as JSON lines
        for channel in channels:
            print(json.dumps(channel.to_dict(), ensure_ascii=False))
        
    except Exception as e:
        click.echo(f"Error: Failed to retrieve channels: {e}", err=True)
        raise