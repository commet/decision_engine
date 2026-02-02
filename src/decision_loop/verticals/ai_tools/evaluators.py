"""
AI Tool Selection Evaluators

Concrete implementations of BackwardEvaluator and ForwardSanityChecker
for the AI tool selection domain.
"""

from typing import Any, Optional

from decision_loop.core.evaluators import BackwardEvaluator, ForwardSanityChecker
from decision_loop.core.models import Option, Terminal, CurrentState


class AIToolBackwardEvaluator(BackwardEvaluator):
    """
    Backward Evaluator for AI Tool Selection.

    Compares each Terminal's criteria against Option's features
    to calculate fit score.
    """

    def evaluate(self, option: Option, terminal: Terminal) -> tuple[float, dict[str, float]]:
        """
        Evaluate how well an AI tool option fits a terminal's criteria.

        Args:
            option: AI tool option with features
            terminal: Terminal with criteria requirements

        Returns:
            (score, details) where score is 0.0~1.0 and details shows
            individual criterion scores
        """
        features = option.features
        criteria = terminal.criteria
        details: dict[str, float] = {}
        scores: list[float] = []

        for criterion_key, criterion_value in criteria.items():
            score = self._evaluate_criterion(criterion_key, criterion_value, features)
            details[criterion_key] = score
            scores.append(score)

        # Average score (all criteria equally weighted)
        final_score = sum(scores) / len(scores) if scores else 0.0

        return final_score, details

    def _evaluate_criterion(
        self,
        key: str,
        required: Any,
        features: dict[str, Any]
    ) -> float:
        """
        Evaluate a single criterion.

        Criterion type handling:
        - min_xxx: features[xxx] >= required
        - max_xxx: features[xxx] <= required
        - preferred_xxx: features[xxx] in required (list) or == required
        - exact match: features[xxx] == required

        Args:
            key: Criterion key (e.g., "min_capability_breadth")
            required: Required value
            features: Option's features dict

        Returns:
            Score 0.0 ~ 1.0
        """
        if key.startswith("min_"):
            feature_key = key[4:]  # Remove "min_"
            actual = features.get(feature_key, 0)

            if isinstance(required, bool):
                return 1.0 if actual == required else 0.0

            # Continuous score: how much is satisfied
            if isinstance(actual, bool):
                return 1.0 if actual else 0.0

            if actual >= required:
                return 1.0
            elif actual <= 0:
                return 0.0
            else:
                return actual / required  # Partial fulfillment

        elif key.startswith("max_"):
            feature_key = key[4:]
            actual = features.get(feature_key, float('inf'))

            if actual <= required:
                return 1.0
            else:
                # Penalize based on overage
                if required == 0:
                    return 0.0
                overage = (actual - required) / required
                return max(0.0, 1.0 - overage)

        elif key.startswith("preferred_"):
            feature_key = key[10:]
            actual = features.get(feature_key)

            if isinstance(required, list):
                return 1.0 if actual in required else 0.3  # Non-preferred still gets partial score
            else:
                return 1.0 if actual == required else 0.3

        else:
            # Exact match
            actual = features.get(key)
            if isinstance(required, bool):
                return 1.0 if actual == required else 0.0
            return 1.0 if actual == required else 0.0


class AIToolForwardChecker(ForwardSanityChecker):
    """
    Forward Sanity Checker for AI Tool Selection.

    Evaluates feasibility based on current state (time, budget,
    learning capacity, constraints).
    """

    # Weight for each factor
    FACTOR_WEIGHTS = {
        "time_feasibility": 0.3,
        "budget_feasibility": 0.25,
        "learning_feasibility": 0.25,
        "constraint_compliance": 0.2,
    }

    def should_eliminate(
        self,
        option: Option,
        current_state: CurrentState
    ) -> tuple[bool, Optional[str]]:
        """
        Check for hard constraint violations that require elimination.

        Args:
            option: AI tool option
            current_state: Current state with constraints

        Returns:
            (should_eliminate, reason)
        """
        constraints = current_state.constraints
        features = option.features

        # API required but not available
        if constraints.get("must_have_api") and not features.get("api_availability"):
            return True, "API required but not available"

        # High data sensitivity but low privacy
        if constraints.get("data_sensitivity") == "high":
            if features.get("data_privacy", 0) < 0.7:
                return True, "Data privacy insufficient for high sensitivity"

        # Budget exceeded (no free tier and cost > 2x budget)
        budget = current_state.resources.get("monthly_budget_usd", float('inf'))
        cost = features.get("monthly_cost_usd", 0)
        has_free = features.get("has_free_tier", False)

        if not has_free and cost > budget * 2:
            return True, f"Cost ${cost}/mo exceeds budget ${budget}/mo by too much"

        return False, None

    def evaluate(
        self,
        option: Option,
        current_state: CurrentState
    ) -> tuple[float, dict[str, float]]:
        """
        Soft evaluation: calculate score for each factor and weighted sum.

        Args:
            option: AI tool option
            current_state: Current state

        Returns:
            (total_score, details)
        """
        details: dict[str, float] = {}

        # 1. Time feasibility
        details["time_feasibility"] = self._eval_time(option, current_state)

        # 2. Budget feasibility
        details["budget_feasibility"] = self._eval_budget(option, current_state)

        # 3. Learning feasibility
        details["learning_feasibility"] = self._eval_learning(option, current_state)

        # 4. Constraint compliance
        details["constraint_compliance"] = self._eval_constraints(option, current_state)

        # Weighted sum
        total = sum(
            self.FACTOR_WEIGHTS[k] * v
            for k, v in details.items()
        )

        return total, details

    def _eval_time(self, option: Option, state: CurrentState) -> float:
        """Evaluate time required for learning vs available time."""
        available = state.resources.get("available_hours_per_week", 5)
        learning_curve = option.features.get("learning_curve", 0.5)

        # learning_curve higher = easier = less time needed
        # Rough estimate: hard tool (0.2) needs ~10 hrs/week, easy tool (0.9) needs ~2 hrs/week
        estimated_hours_needed = 10 * (1 - learning_curve) + 2

        if available >= estimated_hours_needed:
            return 1.0
        else:
            return available / estimated_hours_needed

    def _eval_budget(self, option: Option, state: CurrentState) -> float:
        """Evaluate monthly cost vs budget."""
        budget = state.resources.get("monthly_budget_usd", 50)
        cost = option.features.get("monthly_cost_usd", 0)
        has_free = option.features.get("has_free_tier", False)

        if has_free or cost == 0:
            return 1.0
        elif cost <= budget:
            return 1.0
        elif cost <= budget * 1.5:
            return 0.7
        elif cost <= budget * 2:
            return 0.4
        else:
            return 0.1

    def _eval_learning(self, option: Option, state: CurrentState) -> float:
        """Evaluate learning difficulty vs tolerance."""
        max_difficulty = state.constraints.get("max_learning_curve", 0.3)
        # learning_curve: high = easy, low = hard
        # actual_difficulty: 0 = easy, 1 = hard
        actual_difficulty = 1 - option.features.get("learning_curve", 0.5)

        if actual_difficulty <= max_difficulty:
            return 1.0
        else:
            overage = actual_difficulty - max_difficulty
            return max(0.2, 1.0 - overage * 2)

    def _eval_constraints(self, option: Option, state: CurrentState) -> float:
        """Evaluate other soft constraints."""
        score = 1.0

        # Compatibility with existing stack
        existing = state.resources.get("existing_stack", [])
        integration = option.features.get("integration_flexibility", 0.5)
        if existing:
            score *= (0.5 + 0.5 * integration)

        # Risk tolerance vs actual risk
        risk_tolerance = state.preferences.get("risk_tolerance", 0.5)
        vendor_stability = option.features.get("vendor_stability", 0.5)
        if vendor_stability < risk_tolerance:
            score *= 0.8

        return score
