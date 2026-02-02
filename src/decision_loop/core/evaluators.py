"""
Abstract evaluator interfaces for the Decision Loop Engine.

These interfaces define the contract for backward and forward evaluation.
Concrete implementations are provided by verticals.
"""

from abc import ABC, abstractmethod
from typing import Optional

from decision_loop.core.models import Option, Terminal, CurrentState


class BackwardEvaluator(ABC):
    """
    Abstract class that evaluates Option fit based on Terminal criteria.

    Backward evaluation answers the question:
    "If we want to reach this Terminal, how well does this Option fit?"
    """

    @abstractmethod
    def evaluate(self, option: Option, terminal: Terminal) -> tuple[float, dict[str, float]]:
        """
        Evaluate how well an option fits a terminal's criteria.

        Args:
            option: The Option to evaluate
            terminal: The Terminal to use as criteria

        Returns:
            (score, details)
            - score: 0.0 ~ 1.0 fit score
            - details: {criterion_name: individual_score} detailed scores
        """
        pass


class ForwardSanityChecker(ABC):
    """
    Abstract class that evaluates Option feasibility based on current state.

    Forward evaluation answers the question:
    "Given my current state, can I actually execute this Option?"
    """

    @abstractmethod
    def evaluate(self, option: Option, current_state: CurrentState) -> tuple[float, dict[str, float]]:
        """
        Evaluate feasibility of an option given current state.

        Args:
            option: The Option to evaluate
            current_state: The current state

        Returns:
            (score, details)
            - score: 0.0 ~ 1.0 feasibility score
            - details: {factor_name: individual_score} detailed scores
        """
        pass

    def should_eliminate(
        self, option: Option, current_state: CurrentState
    ) -> tuple[bool, Optional[str]]:
        """
        Determine if an Option should be completely eliminated.

        This is for hard constraints that make an option completely unfeasible.

        Returns:
            (should_eliminate, reason)
        """
        return False, None
