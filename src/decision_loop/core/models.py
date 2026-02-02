"""
Core data models for the Decision Loop Engine.

These models are domain-agnostic and can be used across different verticals.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any


@dataclass
class DecisionContext:
    """
    Metadata object containing the background context of a decision.

    The engine does not interpret or score this.
    It exists for humans to read and understand the context.
    """
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass
class Terminal:
    """
    A terminal state to reach.

    Note: This is a 'perspective', not a 'correct answer'.
    Multiple terminals represent different judgment criteria,
    not a good-to-bad spectrum.
    """
    id: str
    name: str
    description: str
    weight: float
    criteria: dict[str, Any]

    def __post_init__(self):
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError(f"weight must be 0.0~1.0, got {self.weight}")


@dataclass
class Option:
    """
    A candidate option that can be chosen.

    The features dict is freely extensible and varies by vertical.
    """
    id: str
    name: str
    description: str
    features: dict[str, Any]
    metadata: Optional[dict[str, Any]] = None


@dataclass
class CurrentState:
    """
    The current state of the decision-making subject.

    ForwardSanityChecker reads this to evaluate feasibility.
    """
    resources: dict[str, Any]
    constraints: dict[str, Any]
    preferences: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EvaluationResult:
    """
    Evaluation result for a single Option.

    Records all scores and calculation processes transparently.
    """
    option_id: str
    option_name: str

    # Backward scores (per Terminal)
    backward_scores: dict[str, float]
    backward_details: dict[str, dict[str, float]]
    weighted_backward_score: float

    # Forward score
    forward_score: float
    forward_details: dict[str, float]

    # Final score
    total_score: float

    # Flags
    eliminated: bool = False
    elimination_reason: Optional[str] = None


@dataclass
class DecisionLoopResult:
    """
    Complete result of a single Loop execution.
    """
    context: DecisionContext
    terminals: list[Terminal]
    current_state: CurrentState
    evaluations: list[EvaluationResult]
    ranked_options: list[str]  # option_id in order (1st place first)
    run_timestamp: datetime
    loop_iteration: int

    def get_top_n(self, n: int) -> list[EvaluationResult]:
        """Return top n options."""
        top_ids = self.ranked_options[:n]
        return [e for e in self.evaluations if e.option_id in top_ids]

    def get_evaluation(self, option_id: str) -> Optional[EvaluationResult]:
        """Get evaluation for a specific option."""
        for e in self.evaluations:
            if e.option_id == option_id:
                return e
        return None


@dataclass
class LoopState:
    """
    Saves the loop state for later continuation.
    """
    context: DecisionContext
    terminals: list[Terminal]
    options: list[Option]
    current_state: CurrentState
    history: list[DecisionLoopResult]
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "context": {
                "description": self.context.description,
                "created_at": self.context.created_at.isoformat(),
                "tags": self.context.tags,
                "notes": self.context.notes,
            },
            "terminals": [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "weight": t.weight,
                    "criteria": t.criteria,
                }
                for t in self.terminals
            ],
            "options": [
                {
                    "id": o.id,
                    "name": o.name,
                    "description": o.description,
                    "features": o.features,
                    "metadata": o.metadata,
                }
                for o in self.options
            ],
            "current_state": {
                "resources": self.current_state.resources,
                "constraints": self.current_state.constraints,
                "preferences": self.current_state.preferences,
                "timestamp": self.current_state.timestamp.isoformat(),
            },
            "history_count": len(self.history),
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], options: list[Option]) -> "LoopState":
        """Create from dictionary."""
        context = DecisionContext(
            description=data["context"]["description"],
            created_at=datetime.fromisoformat(data["context"]["created_at"]),
            tags=data["context"].get("tags", []),
            notes=data["context"].get("notes"),
        )

        terminals = [
            Terminal(
                id=t["id"],
                name=t["name"],
                description=t["description"],
                weight=t["weight"],
                criteria=t["criteria"],
            )
            for t in data["terminals"]
        ]

        current_state = CurrentState(
            resources=data["current_state"]["resources"],
            constraints=data["current_state"]["constraints"],
            preferences=data["current_state"]["preferences"],
            timestamp=datetime.fromisoformat(data["current_state"]["timestamp"]),
        )

        return cls(
            context=context,
            terminals=terminals,
            options=options,
            current_state=current_state,
            history=[],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
        )
