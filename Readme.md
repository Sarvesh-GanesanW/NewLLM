Overview
Claude provides a conversational interface powered by Claude AI to have natural conversations. It maintains conversation state and context using a ConversationMemory class. Conversations are persisted to S3 for storage and recall. Metadata about conversations is stored in a PostgreSQL database.

Key components:

main.py: Main Flask app with API endpoints
conversation_memory.py: Manages conversation state and context
s3_utils.py: Utilities for saving and loading conversations to S3
database_utils.py: Functions for managing conversation metadata in PostgreSQL
Conversation State
The ConversationMemory class in conversation_memory.py handles tracking state for a conversation. It stores a log of all messages and speakers in the conversation, maintaining context. Old entries are removed once a maximum number of tokens is reached to limit memory usage.

Key methods:

update_memory(): Adds a new message to the memory log.
get_current_context(): Gets the recent context for the conversation.
to_json(): Serializes the memory log to JSON.
The main.py initializes a ConversationMemory instance to track state for each unique conversation.

Conversation Storage
Conversations are persisted to S3 for storage using utilities in s3_utils.py.

upload_conversation_to_s3(): Uploads the ConversationMemory log to an S3 bucket as a JSON file.
get_s3_file_content(): Retrieves and returns the content of a conversation JSON file from S3.
File names are generated based on the unique conversation ID to enable lookup.

Conversation Metadata
Metadata about each conversation is stored in a PostgreSQL database using the database_utils.py module. This allows looking up S3 locations for specific conversations.

The conversations table schema stores:

conversation_id: Unique ID for the conversation
user_id: ID of user who initiated conversation
conversation_name: Optional name for the conversation
s3_file_location: S3 path where conversation content is stored
API Endpoints
main.py implements a Flask application with endpoints to interact with the assistant.

/chat: Primary endpoint that handles sending a message and getting a response from the assistant. Manages the conversation state and memory.
/get_conversation: Retrieves a specific conversation log from S3 based on ID.
/new_chat: Resets the conversation state to start a new chat session.
Claude AI Integration
The main.py module handles integrating with the Claude AI API to generate responses to user messages:

interact_with_bedrock(): Sends a prompt to Claude and returns the response.
get_response(): Gets a Claude response based on current conversation context.
Responses are incorporated into the conversation memory.

Running the App
Requirements:

Claude API key
S3 bucket
PostgreSQL database
Configure credentials and settings in main.py.

Run python main.py to start the Flask app on localhost.


Use these cURL commands to test the flask endpoints:

To test the /chat route, run the command:
    curl -X POST -H "Content-Type: application/json" -d '{"user_input": "Hello", "conversation_name": "My Chat"}' http://localhost:5000/chat

To test the /new_chat route, run the command:
    curl -X POST http://localhost:5000/new_chat -H "Content-Type: application/json" -d '{}'

To test the /get_conversation route, run the command:
    curl -X POST "http://localhost:5001/get_conversation?conversation_id=44f5ef67-6118-4e92-8472-3d05f34b9455"
