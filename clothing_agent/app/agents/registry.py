"""Dynamic specialist-agent registry."""

from __future__ import annotations

from typing import Protocol

from app.agents.schemas import AgentRequest, AgentResult
from app.core.errors import InvalidAgentRequestError
from app.core.routing import AgentName


class SpecialistAgent(Protocol):
    """Public interface implemented by every specialist agent."""

    async def handle(self, request: AgentRequest) -> AgentResult: ...


class AgentRegistry:
    """Resolve target names without hard-coding agent classes in orchestration."""

    def __init__(self) -> None:
        self._agents: dict[AgentName, SpecialistAgent] = {}

    def register(self, name: AgentName, agent: SpecialistAgent) -> None:
        """Register one specialist agent."""

        if name in self._agents:
            raise ValueError(f"Agent already registered: {name}")
        self._agents[name] = agent

    def get(self, name: AgentName) -> SpecialistAgent:
        """Return a specialist agent or raise a stable configuration error."""

        agent = self._agents.get(name)
        if not agent:
            raise InvalidAgentRequestError(
                f"Agent is not registered: {name}", code="AGENT_NOT_REGISTERED"
            )
        return agent

    def names(self) -> list[str]:
        """Return registered names for diagnostics."""

        return sorted(item.value for item in self._agents)
