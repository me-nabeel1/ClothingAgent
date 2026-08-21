"""Agent-facing semantic tool facade over the existing commerce adapter."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .contracts import ToolName
from ..integration.client import CommerceToolAdapter


class AgentTools:
    """Thin semantic tool facade used by Fitzy's runtime.

    This class deliberately contains no commerce calculations. It forwards
    semantic operations to the existing application's API adapter.
    """

    def __init__(self, adapter: CommerceToolAdapter) -> None:
        self._adapter = adapter

    async def execute(self, tool_name: ToolName, parameters: Mapping[str, Any]) -> Any:
        """Execute one semantic operation through the existing API adapter."""

        return await self._adapter.execute(tool_name, parameters)
