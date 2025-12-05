# Telegram Database Storage

A Python package for downloading data from Telegram and storing it in a PostgreSQL database. The database schema is optimized for storing channels, messages, users, and their relationships.

## Features

- **PostgreSQL Integration**: Optimized schema with proper indexes and relationships
- **CLI Tools**: Easy-to-use command-line interface built with Click
- **JSON Lines Format**: Compatible with existing Telegram API tools
- **Environment Configuration**: Database connection via environment variables
- **Error Handling**: Comprehensive error handling and user feedback

## Installation

1. Install dependencies:
```bash
pip install -r datatools/tg/db/requirements.txt
```

2. Set up environment variables:
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_USERNAME=your_username
export DB_PASSWORD=your_password
export DB_DATABASE=telegram_db  # optional, defaults to 'telegram_db'
```

## Database Setup

Initialize the database schema:
```bash
python -m datatools.tg.db init
```

Check database status:
```bash
python -m datatools.tg.db status
```

## Usage

### Channel Management

**Import channels from Telegram API:**
```bash
# Get channels from Telegram API and import to database
python3 -m datatools.tg.api.cli channels --session-slug your_session | \
python -m datatools.tg.db channels put
```

**Export channels from database:**
```bash
# Export all channels in JSON lines format
python -m datatools.tg.db channels get
```

### Message Management

**Import messages from Telegram API:**
```bash
# Get messages from Telegram API and import to database
python3 -m datatools.tg.api.cli messagez --session-slug your_session --channel-id 123456 --limit 1000 | \
python -m datatools.tg.db messages put
```

**Export messages from database:**
```bash
# Export all messages in JSON lines format
python -m datatools.tg.db messages get

# Export messages from specific channel
python -m datatools.tg.db messages get --channel-id 123456

# Export limited number of messages
python -m datatools.tg.db messages get --limit 100
```

**Example workflow:**
```bash
# 1. Get channels from Telegram
python3 -m datatools.tg.api.cli channels --session-slug my_session > channels.jsonl

# 2. Import channels to database
cat channels.jsonl | python -m datatools.tg.db channels put

# 3. Get messages from a specific channel
python3 -m datatools.tg.api.cli messagez --session-slug my_session --channel-id 1761251006 --limit 500 > messages.jsonl

# 4. Import messages to database
cat messages.jsonl | python -m datatools.tg.db messages put

# 5. Verify import
python -m datatools.tg.db messages get --channel-id 1761251006 --limit 10
```

## Database Schema

The database uses the following optimized schema:

### Tables

- **channels**: Store Telegram channel information
  - `id` (BIGINT, PRIMARY KEY): Channel ID
  - `name` (VARCHAR): Channel name
  - `created_at`, `updated_at`: Timestamps

- **users**: Store user information
  - `id` (BIGINT, PRIMARY KEY): User ID
  - `first_name`, `last_name`, `username` (VARCHAR): User details
  - `created_at`, `updated_at`: Timestamps

- **messages**: Store message data
  - `id` (BIGINT, PRIMARY KEY): Message ID
  - `channel_id` (BIGINT, FK): Reference to channels table
  - `user_id` (BIGINT, FK): Reference to users table
  - `content` (TEXT): Message content
  - `message_date` (TIMESTAMP): When message was sent
  - `reply_to_msg_id`, `reply_to_top_id` (BIGINT): Reply relationships
  - `is_forum_topic` (BOOLEAN): Forum topic flag
  - `created_at`, `updated_at`: Timestamps

- **message_extensions**: Additional message metadata
  - `message_id` (BIGINT, PRIMARY KEY, FK): Reference to messages table
  - `viewed`, `summarized` (BOOLEAN): Processing flags
  - `summary` (TEXT): Message summary
  - `is_reply_to`, `is_inferred_reply_to` (BIGINT, FK): Inferred relationships
  - `created_at`, `updated_at`: Timestamps

- **inferred_replies**: Store inferred reply relationships
  - `id` (BIGINT, PRIMARY KEY): Auto-generated ID
  - `message_id` (BIGINT, FK): Source message
  - `reply_to_message_id` (BIGINT, FK): Target message
  - `created_at`: Timestamp

### Indexes

Optimized indexes are created for:
- Channel lookups
- User lookups
- Message date ranges
- Reply relationships
- Inferred reply relationships

## Architecture

```
datatools/tg/db/
├── __init__.py             # Package initialization
├── database_connection.py  # Database connection management
├── cli/                    # Command-line interface
│   ├── __main__.py        # Main CLI entry point
│   ├── channels.py        # Channel command group
│   ├── channels_import.py # Channel import command
│   ├── channels_get.py    # Channel export command
│   ├── messages.py        # Message command group
│   ├── messages_import.py # Message import command
│   ├── messages_get.py    # Message export command
│   └── setup.py           # Database setup commands
├── config/                # Configuration management
│   └── database.py        # Database configuration
├── model/                 # Data models
│   ├── channel.py         # Channel model
│   └── message.py         # Message model
├── repository/            # Data access layer
│   ├── channel_repository.py # Channel repository
│   └── message_repository.py # Message repository
├── sql/                   # SQL scripts
│   └── create_tables.sql  # Table creation script
├── doc/                   # Documentation
│   ├── README.md          # This file
│   ├── GOAL.md            # Project goals
│   └── AGENTS.md          # Development guidelines
└── requirements.txt       # Dependencies
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_HOST` | No | localhost | PostgreSQL host |
| `DB_PORT` | No | 5432 | PostgreSQL port |
| `DB_USERNAME` | Yes | - | Database username |
| `DB_PASSWORD` | Yes | - | Database password |
| `DB_DATABASE` | No | telegram_db | Database name |

## Error Handling

The application provides clear error messages for common issues:

- **Missing environment variables**: Clear indication of required variables
- **Database connection failures**: Connection troubleshooting information
- **Invalid JSON input**: Line-by-line parsing with error reporting
- **Database constraint violations**: Proper handling of duplicate entries

## Data Compatibility

The message import functionality is fully compatible with the JSON lines output from:
- `python3 -m datatools.tg.api.cli messagez` command
- Supports both "Message" and "MessageService" types
- Handles complex nested structures (peer_id, from_id, reply_to, etc.)
- Preserves essential message metadata while optimizing for database storage

## Future Enhancements

- User management commands
- Data validation and sanitization
- Comprehensive unit tests
- Performance optimizations
- Migration scripts for schema updates
- Message search and filtering capabilities

## Contributing

When adding new features:

1. Update the database schema in `sql/create_tables.sql`
2. Create corresponding data models in `model/`
3. Implement repositories in `repository/`
4. Add CLI commands in `cli/`
5. Update this documentation
6. Add tests for new functionality

## Troubleshooting

**Connection Issues:**
```bash
# Test database connection
python -m datatools.tg.db status
```

**Import Issues:**
```bash
# Check JSON format
head -1 your_file.jsonl | python -m json.tool
```

**Schema Issues:**
```bash
# Reinitialize database
python -m datatools.tg.db init
```

**Message Import Issues:**
```bash
# Test with a small sample first
head -10 messages.jsonl | python -m datatools.tg.db messages put