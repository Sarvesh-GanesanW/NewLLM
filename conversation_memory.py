import datetime
import json

class ConversationMemory:
    def __init__(self, max_tokens=200000):
        self.max_tokens = max_tokens
        self.memory = []
        self.current_token_count = 0

    def estimate_tokens(self, text):
        return len(text.split())

    def update_memory(self, speaker, message):
        timestamp = datetime.datetime.now().isoformat()
        entry = {'timestamp': timestamp, 'speaker': speaker, 'message': message}
        self.memory.append(entry)
        new_line_tokens = self.estimate_tokens(message)
        self.current_token_count += new_line_tokens

        while self.current_token_count > self.max_tokens:
            removed_entry = self.memory.pop(0)
            self.current_token_count -= self.estimate_tokens(removed_entry['message'])

    def traverse_memory(self, speaker_filter=None, last_n_messages=None):
        filtered_memory = self.memory

        if speaker_filter:
            # Filter messages by speaker
            filtered_memory = [msg for msg in filtered_memory if msg['speaker'] == speaker_filter]

        if last_n_messages:
            # Get only the last n messages
            filtered_memory = filtered_memory[-last_n_messages:]

        for message in filtered_memory:
            timestamp = message['timestamp']
            speaker = message['speaker']
            text = message['message']
            print(f"{timestamp} - {speaker}: {text}")

    def get_current_context(self):
        context = [f"{entry['speaker']}: {entry['message']}" for entry in self.memory]
        return "\n".join(context)

    def to_json(self):
        return json.dumps(self.memory, indent=4)

    def clear_memory(self):
        self.memory = []
        self.current_token_count = 0
    