"""
Core Decision Loop Engine implementation.

This is the main orchestrator that combines backward and forward
evaluation to produce scored and ranked options.
"""

from datetime import datetime
from typing import Optional

from decision_loop.core.models import (
    DecisionContext,
    Terminal,
    Option,
    CurrentState,
    EvaluationResult,
    DecisionLoopResult,
)
from decision_loop.core.evaluators import BackwardEvaluator, ForwardSanityChecker
from decision_loop.core.scoring import (
    calculate_weighted_backward_score,
    calculate_total_score,
    rank_options,
)


class DecisionLoopEngine:
    """
    Core engine that combines Backward and Forward evaluation to
    score and rank Options.

    This engine:
    1. Makes implicit human judgment explicit
    2. Combines backward (future-fit) and forward (feasibility) thinking
    3. Allows iterative correction over time
    4. Shows its work transparently
    """

    def __init__(
        self,
        backward_evaluator: BackwardEvaluator,
        forward_checker: ForwardSanityChecker
    ):
        """
        Initialize the engine with evaluators.

        Args:
            backward_evaluator: Evaluates options against terminal criteria
            forward_checker: Evaluates option feasibility against current state
        """
        self.backward_evaluator = backward_evaluator
        self.forward_checker = forward_checker
        self.loop_count = 0

    def run(
        self,
        context: DecisionContext,
        options: list[Option],
        terminals: list[Terminal],
        current_state: CurrentState
    ) -> DecisionLoopResult:
        """
        Execute a single decision loop.

        Args:
            context: Background context for the decision
            options: List of candidate options
            terminals: List of terminal states with weights
            current_state: Current state of the decision maker

        Returns:
            DecisionLoopResult with all evaluations and rankings
        """
        self.loop_count += 1
        evaluations = []

        for option in options:
            eval_result = self._evaluate_option(option, terminals, current_state)
            evaluations.append(eval_result)

        ranked = rank_options(evaluations)

        return DecisionLoopResult(
            context=context,
            terminals=terminals,
            current_state=current_state,
            evaluations=evaluations,
            ranked_options=ranked,
            run_timestamp=datetime.now(),
            loop_iteration=self.loop_count
        )

    def _evaluate_option(
        self,
        option: Option,
        terminals: list[Terminal],
        current_state: CurrentState
    ) -> EvaluationResult:
        """
        Evaluate a single Option.

        Process:
        1. Check for hard constraint violations (elimination)
        2. Run backward evaluation against each Terminal
        3. Run forward evaluation against current state
        4. Calculate total score

        Args:
            option: The option to evaluate
            terminals: List of terminals to evaluate against
            current_state: Current state for feasibility check

        Returns:
            Complete EvaluationResult for this option
        """
        # 1. Forward elimination check
        should_eliminate, reason = self.forward_checker.should_eliminate(
            option, current_state
        )

        if should_eliminate:
            return EvaluationResult(
                option_id=option.id,
                option_name=option.name,
                backward_scores={},
                backward_details={},
                weighted_backward_score=0.0,
                forward_score=0.0,
                forward_details={},
                total_score=0.0,
                eliminated=True,
                elimination_reason=reason
            )

        # 2. Backward evaluation (for each Terminal)
        backward_scores: dict[str, float] = {}
        backward_details: dict[str, dict[str, float]] = {}

        for terminal in terminals:
            score, details = self.backward_evaluator.evaluate(option, terminal)
            backward_scores[terminal.id] = score
            backward_details[terminal.id] = details

        weighted_backward = calculate_weighted_backward_score(
            backward_scores, terminals
        )

        # 3. Forward evaluation
        forward_score, forward_details = self.forward_checker.evaluate(
            option, current_state
        )

        # 4. Total score
        total = calculate_total_score(weighted_backward, forward_score)

        return EvaluationResult(
            option_id=option.id,
            option_name=option.name,
            backward_scores=backward_scores,
            backward_details=backward_details,
            weighted_backward_score=weighted_backward,
            forward_score=forward_score,
            forward_details=forward_details,
            total_score=total,
            eliminated=False,
            elimination_reason=None
        )

    def reset_loop_count(self):
        """Reset the loop counter."""
        self.loop_count = 0

    def get_loop_count(self) -> int:
        """Get current loop iteration count."""
        return self.loop_count
