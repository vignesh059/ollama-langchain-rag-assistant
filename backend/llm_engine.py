"""
LLM Engine for Ollama connection management, model verification, and LLM instantiation.
"""

import urllib.request
import json
from typing import List, Tuple, Dict, Any
from langchain_community.chat_models import ChatOllama
from config import DEFAULT_OLLAMA_URL, DEFAULT_MODEL, AVAILABLE_MODELS


class LLMEngine:
    def __init__(self, base_url: str = DEFAULT_OLLAMA_URL, model_name: str = DEFAULT_MODEL):
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self._llm = None

    def check_connection(self) -> Tuple[bool, str, List[str]]:
        """
        Checks if Ollama server is running and returns available models list.
        Returns: (is_online, status_message, list_of_installed_models)
        """
        try:
            url = f"{self.base_url}/api/tags"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    raw_models = [m.get('name', '') for m in data.get('models', [])]
                    clean_models = [m.split(':')[0] for m in raw_models]
                    all_available = list(set(raw_models + clean_models + AVAILABLE_MODELS))
                    return True, "Connected to Ollama", sorted(all_available)
        except Exception as e:
            return False, f"Ollama Offline ({str(e)})", AVAILABLE_MODELS

        return False, "Ollama Unreachable", AVAILABLE_MODELS

    def get_llm(self, model_name: str = None, temperature: float = 0.2) -> ChatOllama:
        """
        Returns a ChatOllama instance for the requested model.
        """
        target_model = model_name or self.model_name
        return ChatOllama(
            base_url=self.base_url,
            model=target_model,
            temperature=temperature
        )


llm_engine_instance = LLMEngine()
