"""API Configuration Settings."""

import os


class Settings:
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_AUTH_ENABLED: bool = os.getenv("API_AUTH_ENABLED", "false").lower() in ["true", "1", "yes"]
    API_AUTH_TOKEN: str = os.getenv("API_AUTH_TOKEN", "")

    CASE_WRITEBACK_ENABLED: bool = os.getenv("CASE_WRITEBACK_ENABLED", "true").lower() in ["true", "1", "yes"]
    TIGERGRAPH_WRITEBACK_ENABLED: bool = os.getenv("TIGERGRAPH_WRITEBACK_ENABLED", "false").lower() in ["true", "1", "yes"]

    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "mock-agent-v1")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")


settings = Settings()
