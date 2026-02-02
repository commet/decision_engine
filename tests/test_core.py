"""
Tests for core Decision Loop Engine components.
"""

import pytest
from datetime import datetime

from decision_loop.core.models import (
    DecisionContext,
    Terminal,
    Option,
    CurrentState,
    EvaluationResult,
)
from decision_loop.core.scoring import (
    calculate_weighted_backward_score,
    calculate_total_score,
    rank_options,
    get_ranking_insights,
)
from decision_loop.core.engine import DecisionLoopEngine
from decision_loop.verticals.ai_tools import (
    AIToolBackwardEvaluator,
    AIToolForwardChecker,
    SAMPLE_AI_TOOLS,
    AI_TOOL_TERMINALS,
)


class TestModels:
    """Test core data models."""

    def test_decision_context_creation(self):
        """Test DecisionContext creation with defaults."""
        ctx = DecisionContext(description="Test context")
        assert ctx.description == "Test context"
        assert ctx.tags == []
        assert ctx.notes is None
        assert isinstance(ctx.created_at, datetime)

    def test_terminal_weight_validation(self):
        """Test Terminal weight must be 0-1."""
        with pytest.raises(ValueError):
            Terminal(
                id="t1",
                name="Test",
                description="Test terminal",
                weight=1.5,
                criteria={}
            )

    def test_terminal_valid_weight(self):
        """Test Terminal with valid weight."""
        t = Terminal(
            id="t1",
            name="Test",
            description="Test terminal",
            weight=0.5,
            criteria={"min_score": 0.7}
        )
        assert t.weight == 0.5
        assert t.criteria["min_score"] == 0.7

    def test_option_creation(self):
        """Test Option creation."""
        opt = Option(
            id="opt1",
            name="Test Option",
            description="A test option",
            features={"score": 0.8, "cost": 10}
        )
        assert opt.id == "opt1"
        assert opt.features["score"] == 0.8

    def test_current_state_timestamp(self):
        """Test CurrentState timestamp default."""
        state = CurrentState(
            resources={"budget": 100},
            constraints={"max_cost": 50},
            preferences={"risk": 0.5}
        )
        assert isinstance(state.timestamp, datetime)


class TestScoring:
    """Test scoring functions."""

    def test_weighted_backward_score(self):
        """Test weighted backward score calculation."""
        terminals = [
            Terminal(id="t1", name="T1", description="", weight=0.6, criteria={}),
            Terminal(id="t2", name="T2", description="", weight=0.4, criteria={}),
        ]
        backward_scores = {"t1": 0.8, "t2": 0.5}

        score = calculate_weighted_backward_score(backward_scores, terminals)

        # (0.6 * 0.8 + 0.4 * 0.5) / (0.6 + 0.4) = (0.48 + 0.2) / 1.0 = 0.68
        assert abs(score - 0.68) < 0.001

    def test_weighted_backward_score_zero_weight(self):
        """Test with zero total weight."""
        terminals = [
            Terminal(id="t1", name="T1", description="", weight=0.0, criteria={}),
        ]
        backward_scores = {"t1": 0.8}

        score = calculate_weighted_backward_score(backward_scores, terminals)
        assert score == 0.0

    def test_total_score_multiplication(self):
        """Test total score is product of backward and forward."""
        assert calculate_total_score(0.8, 0.5) == 0.4
        assert calculate_total_score(1.0, 1.0) == 1.0
        assert calculate_total_score(0.0, 0.9) == 0.0

    def test_rank_options_ordering(self):
        """Test options are ranked by total_score descending."""
        evals = [
            EvaluationResult(
                option_id="a", option_name="A",
                backward_scores={}, backward_details={},
                weighted_backward_score=0.5,
                forward_score=0.5, forward_details={},
                total_score=0.5,
            ),
            EvaluationResult(
                option_id="b", option_name="B",
                backward_scores={}, backward_details={},
                weighted_backward_score=0.8,
                forward_score=0.8, forward_details={},
                total_score=0.8,
            ),
            EvaluationResult(
                option_id="c", option_name="C",
                backward_scores={}, backward_details={},
                weighted_backward_score=0.3,
                forward_score=0.3, forward_details={},
                total_score=0.3,
            ),
        ]

        ranked = rank_options(evals)
        assert ranked == ["b", "a", "c"]

    def test_rank_options_eliminated_last(self):
        """Test eliminated options are ranked last."""
        evals = [
            EvaluationResult(
                option_id="a", option_name="A",
                backward_scores={}, backward_details={},
                weighted_backward_score=0.5,
                forward_score=0.5, forward_details={},
                total_score=0.5,
            ),
            EvaluationResult(
                option_id="b", option_name="B",
                backward_scores={}, backward_details={},
                weighted_backward_score=0.9,
                forward_score=0.9, forward_details={},
                total_score=0.9,
                eliminated=True,
                elimination_reason="Test elimination"
            ),
        ]

        ranked = rank_options(evals)
        assert ranked == ["a", "b"]


class TestAIToolEvaluators:
    """Test AI Tool vertical evaluators."""

    def test_backward_evaluator_min_criterion(self):
        """Test backward evaluator handles min_ criteria."""
        evaluator = AIToolBackwardEvaluator()

        option = Option(
            id="test",
            name="Test",
            description="Test option",
            features={"capability_breadth": 0.8}
        )
        terminal = Terminal(
            id="t1",
            name="T1",
            description="Test terminal",
            weight=0.5,
            criteria={"min_capability_breadth": 0.7}
        )

        score, details = evaluator.evaluate(option, terminal)
        assert score == 1.0  # 0.8 >= 0.7
        assert details["min_capability_breadth"] == 1.0

    def test_backward_evaluator_partial_fulfillment(self):
        """Test backward evaluator returns partial score."""
        evaluator = AIToolBackwardEvaluator()

        option = Option(
            id="test",
            name="Test",
            description="Test option",
            features={"capability_breadth": 0.5}
        )
        terminal = Terminal(
            id="t1",
            name="T1",
            description="Test terminal",
            weight=0.5,
            criteria={"min_capability_breadth": 1.0}
        )

        score, details = evaluator.evaluate(option, terminal)
        assert abs(score - 0.5) < 0.001  # 0.5 / 1.0

    def test_forward_checker_elimination(self):
        """Test forward checker eliminates on hard constraints."""
        checker = AIToolForwardChecker()

        option = Option(
            id="test",
            name="Test",
            description="Test option",
            features={"api_availability": False}
        )
        state = CurrentState(
            resources={},
            constraints={"must_have_api": True},
            preferences={}
        )

        should_eliminate, reason = checker.should_eliminate(option, state)
        assert should_eliminate is True
        assert "API required" in reason

    def test_forward_checker_no_elimination(self):
        """Test forward checker passes valid options."""
        checker = AIToolForwardChecker()

        option = Option(
            id="test",
            name="Test",
            description="Test option",
            features={
                "api_availability": True,
                "data_privacy": 0.8,
                "monthly_cost_usd": 20,
                "has_free_tier": True,
            }
        )
        state = CurrentState(
            resources={"monthly_budget_usd": 50},
            constraints={"must_have_api": True, "data_sensitivity": "high"},
            preferences={}
        )

        should_eliminate, reason = checker.should_eliminate(option, state)
        assert should_eliminate is False


class TestDecisionLoopEngine:
    """Test the main DecisionLoopEngine."""

    def test_engine_run_basic(self):
        """Test basic engine run."""
        engine = DecisionLoopEngine(
            backward_evaluator=AIToolBackwardEvaluator(),
            forward_checker=AIToolForwardChecker()
        )

        context = DecisionContext(description="Test run")
        current_state = CurrentState(
            resources={"available_hours_per_week": 5, "monthly_budget_usd": 30},
            constraints={"must_have_api": False, "data_sensitivity": "medium"},
            preferences={"risk_tolerance": 0.5}
        )

        result = engine.run(
            context,
            SAMPLE_AI_TOOLS[:3],  # Just first 3 options
            AI_TOOL_TERMINALS,
            current_state
        )

        assert result.loop_iteration == 1
        assert len(result.evaluations) == 3
        assert len(result.ranked_options) == 3

    def test_engine_loop_count_increments(self):
        """Test engine loop count increments."""
        engine = DecisionLoopEngine(
            backward_evaluator=AIToolBackwardEvaluator(),
            forward_checker=AIToolForwardChecker()
        )

        context = DecisionContext(description="Test")
        state = CurrentState(
            resources={"available_hours_per_week": 5, "monthly_budget_usd": 30},
            constraints={},
            preferences={}
        )

        result1 = engine.run(context, SAMPLE_AI_TOOLS[:2], AI_TOOL_TERMINALS, state)
        result2 = engine.run(context, SAMPLE_AI_TOOLS[:2], AI_TOOL_TERMINALS, state)

        assert result1.loop_iteration == 1
        assert result2.loop_iteration == 2

    def test_engine_evaluates_all_options(self):
        """Test engine evaluates all provided options."""
        engine = DecisionLoopEngine(
            backward_evaluator=AIToolBackwardEvaluator(),
            forward_checker=AIToolForwardChecker()
        )

        context = DecisionContext(description="Test")
        state = CurrentState(
            resources={"available_hours_per_week": 10, "monthly_budget_usd": 100},
            constraints={},
            preferences={}
        )

        result = engine.run(context, SAMPLE_AI_TOOLS, AI_TOOL_TERMINALS, state)

        assert len(result.evaluations) == len(SAMPLE_AI_TOOLS)
        for e in result.evaluations:
            assert e.total_score >= 0
            assert e.total_score <= 1


class TestSampleData:
    """Test sample data integrity."""

    def test_sample_options_have_required_fields(self):
        """Test all sample options have required feature fields."""
        required_fields = [
            "capability_breadth",
            "learning_curve",
            "monthly_cost_usd",
            "has_free_tier",
            "vendor_stability",
        ]

        for option in SAMPLE_AI_TOOLS:
            for field in required_fields:
                assert field in option.features, f"{option.id} missing {field}"

    def test_sample_terminals_weights_valid(self):
        """Test sample terminal weights are valid."""
        total_weight = sum(t.weight for t in AI_TOOL_TERMINALS)
        assert abs(total_weight - 1.0) < 0.001

    def test_sample_terminals_have_criteria(self):
        """Test all sample terminals have criteria."""
        for terminal in AI_TOOL_TERMINALS:
            assert len(terminal.criteria) > 0
