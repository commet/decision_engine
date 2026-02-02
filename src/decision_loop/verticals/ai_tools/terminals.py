"""
Sample Terminal Definitions for AI Tool Selection

Three recommended terminals representing different judgment criteria,
not a good-to-bad spectrum.
"""

from decision_loop.core.models import Terminal


AI_TOOL_TERMINALS = [
    Terminal(
        id="T1_ideal",
        name="Ideal Future",
        description=(
            "AI tool completely mastered, productivity maximized. "
            "The tool becomes an extension of myself, handling complex tasks naturally. "
            "Can quickly adapt when new features are released."
        ),
        weight=0.3,
        criteria={
            "min_capability_breadth": 0.8,
            "min_capability_depth": 0.7,
            "min_ecosystem_size": 0.7,
            "min_customization": 0.6,
            "preferred_cost_model": ["freemium", "subscription"],
            "min_momentum": 0.7,
        }
    ),
    Terminal(
        id="T2_realistic",
        name="Realistic Future",
        description=(
            "Stably utilizing AI tool in daily work. "
            "Not using all features, but proficient with core functionality. "
            "Occasionally feel limitations but generally satisfied."
        ),
        weight=0.5,
        criteria={
            "min_capability_breadth": 0.6,
            "min_learning_curve": 0.5,  # Not too hard
            "min_documentation_quality": 0.6,
            "min_vendor_stability": 0.7,
            "max_monthly_cost_usd": 50,
        }
    ),
    Terminal(
        id="T3_minimum",
        name="Regret-Minimized Future",
        description=(
            "At minimum, a choice I won't regret. "
            "Avoid situations where tool suddenly disappears, prices skyrocket, "
            "or learned skills become useless."
        ),
        weight=0.2,
        criteria={
            "min_vendor_stability": 0.8,
            "min_lock_in_risk": 0.6,  # Low lock-in risk
            "min_data_privacy": 0.7,
            "has_free_tier": True,  # At least can start free
            "min_community_support": 0.5,
        }
    ),
]


def get_terminal_by_id(terminal_id: str) -> Terminal | None:
    """Get a terminal by its ID."""
    for terminal in AI_TOOL_TERMINALS:
        if terminal.id == terminal_id:
            return terminal
    return None


def create_custom_terminals(
    ideal_weight: float = 0.3,
    realistic_weight: float = 0.5,
    minimum_weight: float = 0.2
) -> list[Terminal]:
    """
    Create terminal set with custom weights.

    Args:
        ideal_weight: Weight for ideal terminal (default 0.3)
        realistic_weight: Weight for realistic terminal (default 0.5)
        minimum_weight: Weight for minimum terminal (default 0.2)

    Returns:
        List of terminals with adjusted weights
    """
    terminals = []
    for t in AI_TOOL_TERMINALS:
        if t.id == "T1_ideal":
            weight = ideal_weight
        elif t.id == "T2_realistic":
            weight = realistic_weight
        else:
            weight = minimum_weight

        terminals.append(Terminal(
            id=t.id,
            name=t.name,
            description=t.description,
            weight=weight,
            criteria=t.criteria.copy()
        ))

    return terminals
