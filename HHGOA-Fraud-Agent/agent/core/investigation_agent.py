"""LLM Provider Interface and Agent Reasoning Abstraction."""

import os
import json
from typing import Any, Dict, List, Optional


class LLMProvider:
    """Abstract interface for LLM calls with deterministic mock fallback."""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None, api_key: Optional[str] = None):
        self.provider = provider or os.getenv("LLM_PROVIDER", "mock")
        self.model = model or os.getenv("LLM_MODEL", "mock-agent-v1")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")

    def generate_response(self, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> Dict[str, Any]:
        """Dispatches to configured provider or deterministic mock engine."""
        if self.provider == "mock" or not self.api_key:
            # Deterministic mock mode for local testing without external API dependency
            return {
                "content": "Synthesized graph and case memory evidence with deterministic policy rules.",
                "tokens": 420,
                "provider": "mock",
            }

        # Extensible for OpenAI / Anthropic / Google Gemini APIs
        # Protected: API keys are read strictly from environment variables
        try:
            if self.provider == "openai":
                import openai
                client = openai.OpenAI(api_key=self.api_key)
                resp = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temperature,
                )
                return {
                    "content": resp.choices[0].message.content,
                    "tokens": resp.usage.total_tokens if resp.usage else 500,
                    "provider": "openai",
                }
        except Exception as e:
            return {
                "content": f"LLM invocation failed: {e}. Falling back to deterministic reasoning.",
                "tokens": 0,
                "provider": "mock-fallback",
            }

        return {
            "content": "Deterministic evidence evaluation completed.",
            "tokens": 350,
            "provider": "mock",
        }
