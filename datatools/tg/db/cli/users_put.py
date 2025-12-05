import click
import json
import sys

from datatools.tg.db.config.database import DatabaseConfig
from datatools.tg.db.database_connection import DatabaseConnection
from datatools.tg.db.model.user import User
from datatools.tg.db.repository.user_repository import UserRepository


@click.command()
def users_put():
    """Import users from STDIN in JSON lines format (compatible with channel-participants output)."""
    try:
        # Get database configuration from environment
        config = DatabaseConfig.from_env()
        
        # Create database connection
        db = DatabaseConnection(config)
        
        # Create user repository
        user_repo = UserRepository(db)
        
        # Read JSON lines from STDIN
        users = []
        for line in sys.stdin:
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                    # Extract only the fields we need for the User model
                    # Based on the example, we need: id, first_name, last_name, username
                    user_data = {
                        'id': data['id'],
                        'first_name': data.get('first_name'),
                        'last_name': data.get('last_name'),
                        'username': data.get('username')
                    }
                    user = User.from_dict(user_data)
                    users.append(user)
                except json.JSONDecodeError as e:
                    click.echo(f"Warning: Failed to parse JSON line: {e}", err=True)
                    continue
                except KeyError as e:
                    click.echo(f"Warning: Missing required field {e} in JSON line", err=True)
                    continue
        
        # Save users to database
        saved_count = user_repo.save_batch(users)
        
        click.echo(f"Successfully imported {saved_count} users")
        
    except Exception as e:
        click.echo(f"Error: Failed to import users: {e}", err=True)
        raise