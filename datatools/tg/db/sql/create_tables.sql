-- Database schema for Telegram data storage
-- Tables are designed to store channels, users, and messages with their relationships

-- Channels table
CREATE TABLE IF NOT EXISTS channels (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    username VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id BIGINT PRIMARY KEY,
    channel_id BIGINT,  -- Removed foreign key constraint to allow messages without channels
    user_id BIGINT,     -- Removed foreign key constraint to allow messages without users
    content TEXT,
    message_date TIMESTAMP WITH TIME ZONE,
    reply_to_msg_id BIGINT,
    reply_to_top_id BIGINT,
    is_forum_topic BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Message extensions table for additional metadata
CREATE TABLE IF NOT EXISTS message_extensions (
    message_id BIGINT PRIMARY KEY REFERENCES messages(id) ON DELETE CASCADE,
    viewed BOOLEAN DEFAULT FALSE,
    summary TEXT,
    summarized BOOLEAN DEFAULT FALSE,
    is_reply_to BIGINT REFERENCES messages(id) ON DELETE SET NULL,
    is_inferred_reply_to BIGINT REFERENCES messages(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Inferred replies table for storing inferred reply relationships
CREATE TABLE IF NOT EXISTS inferred_replies (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    message_id BIGINT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    reply_to_message_id BIGINT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_messages_channel_id ON messages(channel_id);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_message_date ON messages(message_date);
CREATE INDEX IF NOT EXISTS idx_messages_reply_to_msg_id ON messages(reply_to_msg_id);
CREATE INDEX IF NOT EXISTS idx_inferred_replies_message_id ON inferred_replies(message_id);
CREATE INDEX IF NOT EXISTS idx_inferred_replies_reply_to_message_id ON inferred_replies(reply_to_message_id);

-- Add foreign key constraints as separate statements (optional, can be added later)
-- These are commented out to allow flexible data import
-- ALTER TABLE messages ADD CONSTRAINT fk_messages_channel_id FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE SET NULL;
-- ALTER TABLE messages ADD CONSTRAINT fk_messages_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;