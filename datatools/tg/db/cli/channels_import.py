import click
import json
import sys

from datatools.tg.db.config.database import DatabaseConfig
from datatools.tg.db.database_connection import DatabaseConnection
from datatools.tg.db.model.channel import Channel
from datatools.tg.db.repository.channel_repository import ChannelRepository


@click.command()
def channels_import():
    """Import channels from STDIN in JSON lines format."""
    try:
        # Get database configuration from environment
        config = DatabaseConfig.from_env()
        
        # Create database connection
        db = DatabaseConnection(config)
        
        # Create channel repository
        channel_repo = ChannelRepository(db)
        
        # Read JSON lines from STDIN
        channels = []
        for line in sys.stdin:
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                    channel = Channel.from_dict(data)
                    channels.append(channel)
                except json.JSONDecodeError as e:
                    click.echo(f"Warning: Failed to parse JSON line: {e}", err=True)
                    continue
        
        # Save channels to database
        saved_count = channel_repo.save_batch(channels)
        
        click.echo(f"Successfully imported {saved_count} channels")
        
    except Exception as e:
        click.echo(f"Error: Failed to import channels: {e}", err=True)
        raise
