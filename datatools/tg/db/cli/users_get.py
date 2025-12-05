import click
import json

from datatools.tg.db.config.database import DatabaseConfig
from datatools.tg.db.database_connection import DatabaseConnection
from datatools.tg.db.repository.user_repository import UserRepository


@click.command()
def users_get():
    """Retrieve all users and output in JSON lines format."""
    try:
        # Get database configuration from environment
        config = DatabaseConfig.from_env()
        
        # Create database connection
        db = DatabaseConnection(config)
        
        # Create user repository
        user_repo = UserRepository(db)
        
        # Get all users from database
        users = user_repo.get_all()
        
        # Output users as JSON lines
        for user in users:
            print(json.dumps(user.to_dict(), ensure_ascii=False))
        
    except Exception as e:
        click.echo(f"Error: Failed to retrieve users: {e}", err=True)
        raise