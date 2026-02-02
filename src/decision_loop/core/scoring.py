"""
Scoring logic for the Decision Loop Engine.

Contains pure functions for calculating weighted backward scores,
total scores, and generating rankings.
"""

from decision_loop.core.models import Terminal, EvaluationResult


def calculate_weighted_backward_score(
    backward_scores: dict[str, float],
    terminals: list[Terminal]
) -> float:
    """
    Calculate weighted sum of backward scores across terminals.

    Formula:
        weighted_backward = Σ (terminal.weight × backward_score[terminal])
                            ─────────────────────────────────────────────
                                        Σ terminal.weight

    Args:
        backward_scores: {terminal_id: score} mapping
        terminals: List of Terminal objects with weights

    Returns:
        Weighted backward score (0.0 ~ 1.0)
    """
    total_weight = sum(t.weight for t in terminals)
    if total_weight == 0:
        return 0.0

    weighted_sum = sum(
        t.weight * backward_scores.get(t.id, 0.0)
        for t in terminals
    )

    return weighted_sum / total_weight


def calculate_total_score(
    weighted_backward_score: float,
    forward_score: float
) -> float:
    """
    Calculate final score as product of backward and forward scores.

    Formula: total = weighted_backward × forward

    Rationale:
    - High future fit but infeasible → approaches 0
    - Feasible but no future meaning → low score
    - Both must be high for high total score (multiplicative)

    Args:
        weighted_backward_score: Weighted backward score (0.0 ~ 1.0)
        forward_score: Forward feasibility score (0.0 ~ 1.0)

    Returns:
        Total score (0.0 ~ 1.0)
    """
    return weighted_backward_score * forward_score


def rank_options(evaluations: list[EvaluationResult]) -> list[str]:
    """
    Generate ranking based on total_score in descending order.

    Eliminated options are placed at the end.

    Args:
        evaluations: List of EvaluationResult objects

    Returns:
        List of option_ids in rank order (1st place first)
    """
    active = [e for e in evaluations if not e.eliminated]
    eliminated = [e for e in evaluations if e.eliminated]

    active_sorted = sorted(active, key=lambda e: e.total_score, reverse=True)

    return [e.option_id for e in active_sorted] + [e.option_id for e in eliminated]


def get_ranking_insights(evaluations: list[EvaluationResult]) -> dict[str, any]:
    """
    Generate insights about the ranking for user feedback.

    Returns:
        Dictionary with various insights about the ranking
    """
    active = [e for e in evaluations if not e.eliminated]
    if len(active) < 2:
        return {"status": "insufficient_options"}

    sorted_active = sorted(active, key=lambda e: e.total_score, reverse=True)
    top_two = sorted_active[:2]
    score_gap = top_two[0].total_score - top_two[1].total_score

    insights = {
        "top_score": top_two[0].total_score,
        "top_option": top_two[0].option_id,
        "second_score": top_two[1].total_score,
        "second_option": top_two[1].option_id,
        "score_gap": score_gap,
        "clear_leader": score_gap > 0.1,
        "high_confidence": top_two[0].total_score >= 0.7,
        "close_race": score_gap <= 0.05,
        "eliminated_count": len([e for e in evaluations if e.eliminated]),
    }

    # Generate status message
    if insights["high_confidence"] and insights["clear_leader"]:
        insights["status"] = "clear_recommendation"
        insights["message"] = f"Clear leader: {top_two[0].option_name}"
    elif insights["close_race"]:
        insights["status"] = "close_race"
        insights["message"] = "Top options are very close - consider adjusting weights"
    elif not insights["high_confidence"]:
        insights["status"] = "low_confidence"
        insights["message"] = "No strong candidates - review terminals or options"
    else:
        insights["status"] = "moderate_confidence"
        insights["message"] = "Reasonable recommendation available"

    return insights
