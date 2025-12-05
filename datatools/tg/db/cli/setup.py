import click
import logging
import os

from datatools.tg.db.config.database import DatabaseConfig
from datatools.tg.db.database_connection import DatabaseConnection

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
def init():
    """Initialize the database schema."""
    try:
        # Get database configuration from environment
        config = DatabaseConfig.from_env()
        
        # Create database connection
        db = DatabaseConnection(config)
        
        # Get the path to the SQL script
        script_path = os.path.join(os.path.dirname(__file__), '..', 'sql', 'create_tables.sql')
        script_path = os.path.abspath(script_path)
        
        # Execute the SQL script
        db.execute_script(script_path)
        
        click.echo("Database schema initialized successfully!")
        logger.info("Database schema initialized successfully")
        
    except Exception as e:
        click.echo(f"Failed to initialize database schema: {e}")
        logger.error(f"Failed to initialize database schema: {e}")
        raise


@click.command()
def status():
    """Check database connection and table status."""
    try:
        # Get database configuration from environment
        config = DatabaseConfig.from_env()
        
        # Create database connection
        db = DatabaseConnection(config)
        
        # Test connection
        db.connect()
        click.echo("Database connection successful!")
        
        # Check if tables exist
        tables = ['channels', 'users', 'messages', 'message_extensions', 'inferred_replies']
        existing_tables = []
        missing_tables = []
        
        for table in tables:
            if db.table_exists(table):
                existing_tables.append(table)
            else:
                missing_tables.append(table)
        
        if existing_tables:
            click.echo(f"Existing tables: {', '.join(existing_tables)}")
        
        if missing_tables:
            click.echo(f"Missing tables: {', '.join(missing_tables)}")
            click.echo("Run 'init' to create missing tables")
        else:
            click.echo("All required tables exist")
            
        db.disconnect()
        
    except Exception as e:
        click.echo(f"Failed to check database status: {e}")
        logger.error(f"Failed to check database status: {e}")
        raise