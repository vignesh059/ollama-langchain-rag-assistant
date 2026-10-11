"""
Conversation Memory Engine for retaining context across chat interactions.
"""

from typing import List, Dict, Any
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage


class MemoryEngine:
    def __init__(self):
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )

    def add_user_message(self, message: str):
        """Adds a human user message to history."""
        self.memory.chat_memory.add_user_message(message)

    def add_ai_message(self, message: str):
        """Adds an AI assistant response to history."""
        self.memory.chat_memory.add_ai_message(message)

    def get_messages(self) -> List[BaseMessage]:
        """Returns raw message objects."""
        return self.memory.chat_memory.messages

    def get_formatted_history(self) -> str:
        """Returns readable string transcript of past conversation."""
        messages = self.get_messages()
        if not messages:
            return "No prior conversation history."
        
        transcript = []
        for msg in messages:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            transcript.append(f"{role}: {msg.content}")
        return "\n".join(transcript)

    def clear(self):
        """Clears all conversation memory."""
        self.memory.clear()


memory_engine_instance = MemoryEngine()
