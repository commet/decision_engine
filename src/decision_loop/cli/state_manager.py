"""
State management for Decision Loop sessions.

Handles saving and loading loop state to enable session continuity.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from decision_loop.core.models import (
    DecisionContext,
    Terminal,
    Option,
    CurrentState,
    DecisionLoopResult,
    LoopState,
)


class StateManager:
    """
    Manages saving and loading of decision loop state.

    Supports YAML and JSON formats.
    """

    def __init__(self, state_dir: str = ".decision_loop"):
        """
        Initialize state manager.

        Args:
            state_dir: Directory to store state files
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)

    def save_state(
        self,
        state: LoopState,
        name: str,
        format: str = "yaml"
    ) -> Path:
        """
        Save loop state to file.

        Args:
            state: LoopState object to save
            name: Name for the state file
            format: File format ('yaml' or 'json')

        Returns:
            Path to saved file
        """
        state.last_updated = datetime.now()
        data = state.to_dict()

        if format == "yaml":
            file_path = self.state_dir / f"{name}.yaml"
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        else:
            file_path = self.state_dir / f"{name}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        return file_path

    def load_state(
        self,
        name: str,
        options: list[Option]
    ) -> Optional[LoopState]:
        """
        Load loop state from file.

        Args:
            name: Name of the state file (without extension)
            options: List of Option objects (options aren't fully serialized)

        Returns:
            LoopState object or None if not found
        """
        yaml_path = self.state_dir / f"{name}.yaml"
        json_path = self.state_dir / f"{name}.json"

        if yaml_path.exists():
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return LoopState.from_dict(data, options)

        elif json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return LoopState.from_dict(data, options)

        return None

    def list_states(self) -> list[str]:
        """
        List all saved states.

        Returns:
            List of state names
        """
        states = set()
        for path in self.state_dir.glob("*.yaml"):
            states.add(path.stem)
        for path in self.state_dir.glob("*.json"):
            states.add(path.stem)
        return sorted(states)

    def delete_state(self, name: str) -> bool:
        """
        Delete a saved state.

        Args:
            name: Name of the state to delete

        Returns:
            True if deleted, False if not found
        """
        yaml_path = self.state_dir / f"{name}.yaml"
        json_path = self.state_dir / f"{name}.json"

        deleted = False
        if yaml_path.exists():
            yaml_path.unlink()
            deleted = True
        if json_path.exists():
            json_path.unlink()
            deleted = True

        return deleted


class ResultExporter:
    """
    Exports decision loop results to various formats.
    """

    @staticmethod
    def to_json(result: DecisionLoopResult) -> str:
        """Export result to JSON string."""
        from decision_loop.core.scoring import get_ranking_insights

        output = {
            "loop_iteration": result.loop_iteration,
            "run_timestamp": result.run_timestamp.isoformat(),
            "context": {
                "description": result.context.description,
                "tags": result.context.tags,
                "created_at": result.context.created_at.isoformat(),
            },
            "terminals": [
                {
                    "id": t.id,
                    "name": t.name,
                    "weight": t.weight,
                    "description": t.description,
                }
                for t in result.terminals
            ],
            "rankings": result.ranked_options,
            "evaluations": [
                {
                    "option_id": e.option_id,
                    "option_name": e.option_name,
                    "backward_scores": e.backward_scores,
                    "backward_details": e.backward_details,
                    "weighted_backward_score": e.weighted_backward_score,
                    "forward_score": e.forward_score,
                    "forward_details": e.forward_details,
                    "total_score": e.total_score,
                    "eliminated": e.eliminated,
                    "elimination_reason": e.elimination_reason,
                }
                for e in result.evaluations
            ],
            "insights": get_ranking_insights(result.evaluations),
        }
        return json.dumps(output, indent=2, ensure_ascii=False)

    @staticmethod
    def to_markdown(result: DecisionLoopResult) -> str:
        """Export result to Markdown string."""
        from decision_loop.core.scoring import get_ranking_insights

        lines = [
            "# Decision Loop Results",
            "",
            f"**Loop Iteration:** {result.loop_iteration}",
            f"**Run Time:** {result.run_timestamp.isoformat()}",
            "",
            "## Context",
            "",
            result.context.description,
            "",
            "## Terminals",
            "",
            "| Terminal | Weight | Description |",
            "|----------|--------|-------------|",
        ]

        for t in result.terminals:
            desc = t.description.replace("\n", " ")[:50] + "..."
            lines.append(f"| {t.name} | {t.weight:.2f} | {desc} |")

        lines.extend([
            "",
            "## Rankings",
            "",
            "| Rank | Option | Backward | Forward | Total | Status |",
            "|------|--------|----------|---------|-------|--------|",
        ])

        for rank, option_id in enumerate(result.ranked_options, 1):
            e = result.get_evaluation(option_id)
            if e:
                status = "ELIMINATED" if e.eliminated else "Active"
                lines.append(
                    f"| {rank} | {e.option_name} | {e.weighted_backward_score:.2f} | "
                    f"{e.forward_score:.2f} | {e.total_score:.2f} | {status} |"
                )

        insights = get_ranking_insights(result.evaluations)
        lines.extend([
            "",
            "## Insights",
            "",
            f"**Status:** {insights.get('message', 'N/A')}",
            "",
        ])

        return "\n".join(lines)

    @staticmethod
    def save(result: DecisionLoopResult, path: str, format: str = "json"):
        """
        Save result to file.

        Args:
            result: DecisionLoopResult to save
            path: Output file path
            format: 'json' or 'markdown'
        """
        if format == "json":
            content = ResultExporter.to_json(result)
        else:
            content = ResultExporter.to_markdown(result)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
