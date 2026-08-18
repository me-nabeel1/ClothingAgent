import logging
from typing import Optional, Any
from app.agent.state import ConversationState
from app.agent.registry import ToolSpec

logger = logging.getLogger(__name__)


class ParameterRequirementsChecker:
    """Checks if tool actions have their primary required parameters before execution."""

    @staticmethod
    async def check(spec: ToolSpec, args: dict, state: ConversationState) -> str | None:
        logger.info(f"[CHECKER GATE INITIATED] Validating payload parameters for tool '{spec.name}'", extra={"tool": spec.name, "payload_args": args})

        if spec.soft_required is not None:
            for field_name, resolver_fn in spec.soft_required.items():
                val = args.get(field_name)
                if val is None or val == "" or val == []:
                    resolved = resolver_fn(state, args)
                    if resolved is not None:
                        args[field_name] = resolved
                        logger.info(f"[CHECKER GATE RESOLVED] Soft-required field '{field_name}' resolved to '{resolved}' for tool '{spec.name}'")

        missing = []
        for field_name, field_info in spec.payload_model.model_fields.items():
            if field_info.is_required():
                val = args.get(field_name)
                if val is None or val == "" or val == []:
                    missing.append(field_name)

        if missing:
            fields_str = ", ".join(missing)
            logger.info(f"[CHECKER GATE INCOMPLETE] Tool '{spec.name}' missing required parameters: {fields_str}", extra={"tool": spec.name, "missing": missing})
            return f"MISSING PARAMETERS for {spec.name}: {fields_str}. INSTRUCTION: Ask the customer for {fields_str} before proceeding with {spec.name}."

        logger.info(f"[CHECKER GATE PASSED] All required parameters present for tool '{spec.name}'", extra={"tool": spec.name})
        return None

