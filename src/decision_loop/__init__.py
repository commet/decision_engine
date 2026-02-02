"""
Decision Loop Engine

A decision-structuring engine that combines backward induction
(future-fit) and forward feasibility checks to help structure
complex decisions across multiple possible futures.

This is not a recommendation system or optimizer.
This is a tool for making implicit human judgment explicit.
"""

__version__ = "0.1.0"

from decision_loop.core.models import (
    DecisionContext,
    Terminal,
    Option,
    CurrentState,
    EvaluationResult,
    DecisionLoopResult,
)
from decision_loop.core.engine import DecisionLoopEngine
from decision_loop.core.evaluators import BackwardEvaluator, ForwardSanityChecker

__all__ = [
    "DecisionContext",
    "Terminal",
    "Option",
    "CurrentState",
    "EvaluationResult",
    "DecisionLoopResult",
    "DecisionLoopEngine",
    "BackwardEvaluator",
    "ForwardSanityChecker",
]
