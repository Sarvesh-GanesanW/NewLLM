# Conversational Assistant API

This readme file provides an in-depth view on the Flask-based API interfacing with Claude AI to create conversational assistants. It includes components for conversation state management, storage on AWS S3, and metadata management using PostgreSQL.

## Components

- `main.py`: Flask application and API endpoints.
- `conversation_memory.py`: Manages conversation state and context.
- `s3_utils.py`: Utilities for interacting with AWS S3.
- `database_utils.py`: PostgreSQL database interaction functions.

## Conversation State

The `ConversationMemory` class in `conversation_memory.py` manages the state of a conversation, storing a log of all messages and speakers, and maintaining the context within a memory limit.

### Key Methods

- `update_memory()`: Adds a new message to the memory log.
- `get_current_context()`: Retrieves recent context for ongoing conversations.
- `to_json()`: Serializes the conversation memory log to JSON.

## Conversation Storage

Conversations are stored in an S3 bucket using the following methods in `s3_utils.py`:

- `upload_conversation_to_s3()`: Uploads the serialized conversation log.
- `get_s3_file_content()`: Fetches a conversation log from S3.

## Conversation Metadata

Metadata is stored in a PostgreSQL database, allowing retrieval of conversation logs based on IDs or other metadata.

### Database Schema

- `conversation_id`: Unique identifier for each conversation.
- `user_id`: Identifier for the user who initiated the conversation.
- `conversation_name`: Name of the conversation (optional).
- `s3_file_location`: Path to the conversation log in S3.

## API Endpoints

- `/chat`: Sends and receives messages.
- `/get_conversation`: Retrieves a conversation based on its ID.
- `/new_chat`: Starts a new chat session.

## Claude AI Integration

Integration with Claude AI is handled in `main.py`, managing the sending of prompts and receiving of responses.

## Running the App

### Requirements

- AWS Bedrock Access
- AWS S3 bucket
- PostgreSQL database

### Configuration

Set up necessary credentials in `main.py`.

### Start the Server

```bash
python main.py
