"""
Python migration draft for `src/tools/ExitPlanModeTool/prompt.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

EXIT_PLAN_MODE_V2_TOOL_PROMPT = "Use exit_plan_mode when the plan is accepted or the session should return to implementation mode."

__all__ = ["EXIT_PLAN_MODE_V2_TOOL_PROMPT"]
