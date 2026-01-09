from collections import defaultdict

class ChatMemory:
    def __init__(self, max_messages=10):
        self.store = defaultdict(list)
        self.max_messages = max_messages

    def add(self, session_id: str, role: str, content: str):
        self.store[session_id].append({
            "role": role,
            "content": content
        })

        # mantém só as últimas N mensagens
        self.store[session_id] = self.store[session_id][-self.max_messages:]

    def get(self, session_id: str):
        return self.store[session_id]