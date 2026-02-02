"""
AI Tools Selection Vertical

The first concrete implementation of the Decision Loop Engine.

Problem space:
- Too many AI tools (Claude, GPT, Gemini, Cursor, v0, Bolt, ...)
- High learning cost for each
- Wrong choice = high switching cost
- "Currently hot" != "right for me"
"""

from decision_loop.verticals.ai_tools.evaluators import (
    AIToolBackwardEvaluator,
    AIToolForwardChecker,
)
from decision_loop.verticals.ai_tools.options import SAMPLE_AI_TOOLS
from decision_loop.verticals.ai_tools.terminals import AI_TOOL_TERMINALS

__all__ = [
    "AIToolBackwardEvaluator",
    "AIToolForwardChecker",
    "SAMPLE_AI_TOOLS",
    "AI_TOOL_TERMINALS",
]
