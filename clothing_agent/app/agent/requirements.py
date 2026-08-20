"""Generic validation of tool requirements before an API call is allowed."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.agent.contracts import RequirementCheckResult, ToolContract


class ToolRequirementChecker:
    """Resolve and validate required tool parameters without calling APIs.

    The checker is deliberately generic.  It does not know what a cart,
    product, branch, or order means.  It only understands the contract saying
    which parameters are required and whether missing values can come from
    state/derived context.
    """

    def check(
        self,
        contract: ToolContract,
        provided_parameters: Mapping[str, Any] | None = None,
        state_values: Mapping[str, Any] | None = None,
        derived_values: Mapping[str, Any] | None = None,
    ) -> RequirementCheckResult:
        """Check whether a tool can execute with the values currently known.

        Values supplied directly for the invocation have highest precedence.
        State values are then used where the contract permits them, followed by
        deterministic derived values.  The method never invents values and
        never calls an external service.
        """

        provided = dict(provided_parameters or {})
        state = dict(state_values or {})
        derived = dict(derived_values or {})

        resolved: dict[str, Any] = {}
        missing: list[str] = []
        invalid: list[str] = []

        for parameter in contract.parameters:
            value_found = False
            value: Any = None

            if self._is_usable(provided.get(parameter.name)):
                value = provided[parameter.name]
                value_found = True
            elif parameter.allow_state_value and self._is_usable(state.get(parameter.name)):
                value = state[parameter.name]
                value_found = True
            elif parameter.allow_derived_value and self._is_usable(derived.get(parameter.name)):
                value = derived[parameter.name]
                value_found = True

            if value_found:
                resolved[parameter.name] = value
            elif parameter.required:
                missing.append(parameter.name)

        if contract.requires_explicit_confirmation:
            confirmation = resolved.get("explicit_confirmation")
            if confirmation is not True:
                invalid.append("explicit_confirmation")

        ready = not missing and not invalid
        reason = None
        if missing:
            reason = "One or more required parameters are missing."
        elif invalid:
            reason = "One or more required parameters are invalid or not confirmed."

        return RequirementCheckResult(
            tool_name=contract.name,
            ready=ready,
            resolved_parameters=resolved,
            missing_parameters=tuple(missing),
            invalid_parameters=tuple(invalid),
            reason=reason,
        )

    @staticmethod
    def _is_usable(value: Any) -> bool:
        """Return whether a value is meaningful enough to satisfy a parameter."""

        if value is None:
            return False
        if isinstance(value, str) and not value.strip():
            return False
        if isinstance(value, (list, tuple, set, dict)) and not value:
            return False
        return True
