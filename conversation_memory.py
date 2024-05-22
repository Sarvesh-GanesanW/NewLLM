import datetime
import json

"""Initializes a ConversationMemory instance to track conversation history.

Args:
  max_tokens: Maximum number of word tokens to store before removing old entries.
"""
class ConversationMemory:
    def __init__(self, max_tokens=200000):
        self.conversation_id = None
        self.max_tokens = max_tokens
        self.memory = []
        self.current_token_count = 0

    """Estimates the number of tokens in the given text.
    
    Tokens are defined as sequences of characters separated by whitespace.
    This provides a rough estimate of the number of tokens for tracking
    memory usage.
    """
    def estimate_tokens(self, text):
        return max(1, len(text) // 4)

    """Updates the conversation memory with a new message.
    
    Adds a new message entry to the memory, tracking metadata
    like conversation ID, user ID, speaker, timestamp. Manages
    memory capacity by removing old entries when max tokens 
    is reached.
    """
    def update_memory(self, conversation_id, user_id, speaker, message, input_token):
        timestamp = datetime.datetime.now().isoformat()
        entry = {
            'conversation_id': conversation_id,
            'user_id': user_id,
            'timestamp': timestamp, 
            'speaker': speaker, 
            'message': message,
            'input_token_count': input_token
        }
        self.memory.append(entry)
        self.current_token_count += input_token

        while self.current_token_count > self.max_tokens:
            removed_entry = self.memory.pop(0)
            self.current_token_count -= self.estimate_tokens(removed_entry['message'])

    """Traverses the conversation memory.
    
    Can filter by speaker and number of most recent messages. 
    Prints details of messages matching filters.
    """
    def traverse_memory(self, speaker_filter=None, last_n_messages=None):
        filtered_memory = self.memory

        if speaker_filter:
            filtered_memory = [msg for msg in filtered_memory if msg['speaker'] == speaker_filter]

        if last_n_messages:
            filtered_memory = filtered_memory[-last_n_messages:]

        for message in filtered_memory:
            timestamp = message['timestamp']
            conv_id = message['conversation_id']
            user = message['user_id']
            speaker = message['speaker']
            text = message['message']
            print(f"ConvID: {conv_id}, UserID: {user}, {timestamp} - {speaker}: {text}")

    """Returns the current context from the conversation memory.
    
    Joins together the most recent messages in the memory by speaker and text 
    to provide current context.
    """
    def get_current_context(self):
        context = [f"{entry['speaker']}: {entry['message']}" for entry in self.memory]
        return "\n".join(context)

    """Converts the conversation memory to JSON format.
    
    Serializes the conversation memory list to a JSON string, using indentation 
    for readability.
    
    Returns:
        str: The conversation memory serialized as a JSON string.
    """
    def to_json(self):
        return json.dumps(self.memory, indent=4)

    """Clears the conversation memory by resetting the memory list and current token count.
    
    This allows the memory to be cleared when it reaches the max token limit, 
    to continue logging new messages.
    """
    def clear_memory(self):
        self.memory = []
        self.current_token_count = 0
