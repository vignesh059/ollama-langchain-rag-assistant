"""
Configuration module for the Chatbot application.
"""

import os

# Ollama Defaults
DEFAULT_OLLAMA_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
AVAILABLE_MODELS = [
    "llama3.2:latest",
    "llama3.2",
    "llama3",
    "llama3:8b",
    "llama2",
    "mistral",
    "gemma2",
    "codellama"
]
DEFAULT_MODEL = "llama3.2:latest"

# RAG Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
RAG_TOP_K = 3
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Attendance Tool Config
DEFAULT_ATTENDANCE_THRESHOLD = 75.0  # Percentage requirement

# Default System Prompt
DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful, accurate, and friendly AI assistant. "
    "You have access to tools: a PDF document search tool (RAG) when a document is uploaded, "
    "a Wikipedia search tool for general knowledge, and an Attendance Calculator tool for class attendance. "
    "Use tools when appropriate. Always be clear and informative."
)
