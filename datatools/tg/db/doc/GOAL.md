# Project Goal

Develop a robust application for downloading Telegram data and storing it in a PostgreSQL database with an optimized schema for channels, messages, and user relationships.

## Architecture

- **Package**: `datatools.tg.db` 
- **Database**: PostgreSQL with raw SQL for performance
- **CLI Framework**: Click-based command-line interface
- **Configuration**: Environment variable-based database connection

## Core Features

### CLI Commands
- `channels put`: Import channels from STDIN (JSON lines format)
- `channels get`: Export channels to STDOUT (JSON lines format)
- `messages put`: Import messages from STDIN (JSON lines format, compatible with messagez.py output)
- `messages get`: Export messages to STDOUT (JSON lines format, with optional filtering)
- `init`: Initialize database schema
- `status`: Check database connection and table status

### Database Schema
Optimized tables for channels, users, messages, message extensions, and inferred reply relationships with proper indexes and flexible foreign key constraints.

### Integration
Seamless integration with existing `datatools.tg.api.cli` tools for data pipeline workflows:
- Compatible with `channels` command output for channel import
- Compatible with `messagez` command output for message import

## Environment Configuration

Required environment variables:
- `DB_HOST`, `DB_PORT`: Database connection details
- `DB_USERNAME`, `DB_PASSWORD`: Authentication credentials
- `DB_DATABASE`: Target database name (optional)
