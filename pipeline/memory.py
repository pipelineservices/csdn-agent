class ConversationMemory:
    def __init__(self):
        self.history = []

    def add_user(self, text: str):
        self.history.append({"role": "user", "content": text})

    def add_assistant(self, text: str):
        self.history.append({"role": "assistant", "content": text})

    def get_history(self):
        return self.history[-10:]   # limit last N messages

