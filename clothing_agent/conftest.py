"""Pytest configuration for clothing_agent tests."""
import sys
from pathlib import Path

root_dir = str(Path(__file__).resolve().parent.parent)
clothing_agent_dir = str(Path(__file__).resolve().parent)

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if clothing_agent_dir not in sys.path:
    sys.path.insert(0, clothing_agent_dir)

# Ensure 'app' module maps to clothing_agent
for key in list(sys.modules.keys()):
    if key == "app" or key.startswith("app."):
        del sys.modules[key]
