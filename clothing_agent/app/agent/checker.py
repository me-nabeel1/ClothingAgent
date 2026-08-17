from typing import Optional, Any
from app.agent.state import ConversationState
from app.agent.registry import ToolSpec

class ParameterRequirementsChecker:
    """Checks if tool actions have their primary required parameters before execution."""

    @staticmethod
    async def check(spec: ToolSpec, args: dict, state: ConversationState) -> str | None:
        if spec.soft_required is not None:
            for field_name, resolver_fn in spec.soft_required.items():
                val = args.get(field_name)
                if val is None or val == "" or val == []:
                    resolved = resolver_fn(state, args)
                    if resolved is not None:
                        args[field_name] = resolved

        missing = []
        for field_name, field_info in spec.payload_model.model_fields.items():
            if field_info.is_required():
                val = args.get(field_name)
                if val is None or val == "" or val == []:
                    missing.append(field_name)

        if missing:
            fields_str = ", ".join(missing)
            return f"MISSING PARAMETERS for {spec.name}: {fields_str}. INSTRUCTION: Ask the customer for {fields_str} before proceeding with {spec.name}."

        return None

