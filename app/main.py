"""Re-export FastAPI app from root main.py for backward compatibility."""

from main import app, config

__all__ = ["app", "config"]
