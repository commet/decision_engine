"""
CLI interface for the Decision Loop Engine.

Usage:
    decision-loop run --config configs/ai_tools_example.yaml
    decision-loop interactive
    decision-loop run --config configs/ai_tools_example.yaml --output json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from decision_loop.core.models import (
    DecisionContext,
    Terminal,
    Option,
    CurrentState,
    EvaluationResult,
    DecisionLoopResult,
    LoopState,
)
from decision_loop.core.engine import DecisionLoopEngine
from decision_loop.core.scoring import get_ranking_insights
from decision_loop.verticals.ai_tools import (
    AIToolBackwardEvaluator,
    AIToolForwardChecker,
    SAMPLE_AI_TOOLS,
    AI_TOOL_TERMINALS,
)

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_config(config: dict) -> tuple[DecisionContext, list[Terminal], CurrentState, list[Option]]:
    """Parse configuration into model objects."""
    # Context
    context = DecisionContext(
        description=config["context"]["description"],
        tags=config["context"].get("tags", []),
        notes=config["context"].get("notes"),
    )

    # Terminals
    terminals = []
    for t in config["terminals"]:
        terminals.append(Terminal(
            id=t["id"],
            name=t["name"],
            description=t["description"],
            weight=t["weight"],
            criteria=t["criteria"],
        ))

    # Current State
    cs = config["current_state"]
    current_state = CurrentState(
        resources=cs["resources"],
        constraints=cs["constraints"],
        preferences=cs["preferences"],
    )

    # Options
    options_source = config.get("options_source", "builtin")
    if options_source == "builtin":
        options = SAMPLE_AI_TOOLS
    else:
        # Load from file (future enhancement)
        options = SAMPLE_AI_TOOLS

    return context, terminals, current_state, options


def format_score(score: float) -> str:
    """Format score for display."""
    return f"{score:.2f}"


def print_results_rich(result: DecisionLoopResult):
    """Print results using rich library."""
    console = Console()

    # Header
    console.print()
    console.print(Panel(
        f"[bold]Decision Loop Results[/bold]\n"
        f"Loop Iteration: {result.loop_iteration}",
        title="Decision Loop Engine",
        border_style="blue"
    ))

    # Context
    console.print(f"\n[bold]Context:[/bold] {result.context.description[:100]}...")

    # Terminals
    console.print("\n[bold]Terminals:[/bold]")
    terminal_text = "  "
    for t in result.terminals:
        terminal_text += f"{t.name} ({t.weight:.2f})  |  "
    console.print(terminal_text.rstrip("  |  "))

    # Main results table
    console.print()
    table = Table(title="Ranked Options", show_header=True, header_style="bold cyan")
    table.add_column("Rank", justify="center", width=6)
    table.add_column("Option", width=20)
    table.add_column("Backward", justify="center", width=10)
    table.add_column("Forward", justify="center", width=10)
    table.add_column("Total", justify="center", width=10)
    table.add_column("Notes", width=30)

    for rank, option_id in enumerate(result.ranked_options, 1):
        eval_result = result.get_evaluation(option_id)
        if eval_result:
            notes = ""
            if eval_result.eliminated:
                notes = f"[red]ELIMINATED: {eval_result.elimination_reason}[/red]"
            elif eval_result.weighted_backward_score < 0.5:
                notes = "[yellow]Low future fit[/yellow]"
            elif eval_result.forward_score < 0.5:
                notes = "[yellow]Feasibility concerns[/yellow]"

            style = "dim" if eval_result.eliminated else None
            table.add_row(
                str(rank),
                eval_result.option_name,
                format_score(eval_result.weighted_backward_score),
                format_score(eval_result.forward_score),
                format_score(eval_result.total_score),
                notes,
                style=style
            )

    console.print(table)

    # Insights
    insights = get_ranking_insights(result.evaluations)
    console.print(f"\n[bold]Status:[/bold] {insights.get('message', 'N/A')}")

    # Detailed breakdown for top 3
    console.print("\n[bold]Detailed Breakdown (Top 3):[/bold]")
    for option_id in result.ranked_options[:3]:
        eval_result = result.get_evaluation(option_id)
        if eval_result and not eval_result.eliminated:
            console.print(f"\n  [cyan]{eval_result.option_name}[/cyan]")
            console.print("    Backward by Terminal:")
            for t in result.terminals:
                score = eval_result.backward_scores.get(t.id, 0)
                details = eval_result.backward_details.get(t.id, {})
                detail_str = ", ".join(f"{k[:8]}:{v:.1f}" for k, v in list(details.items())[:3])
                console.print(f"      {t.name}: {score:.2f} ({detail_str})")

            console.print("    Forward:")
            forward_str = " | ".join(f"{k}: {v:.2f}" for k, v in eval_result.forward_details.items())
            console.print(f"      {forward_str}")


def print_results_plain(result: DecisionLoopResult):
    """Print results in plain text format."""
    print("\n" + "=" * 60)
    print("Decision Loop Results")
    print(f"Loop Iteration: {result.loop_iteration}")
    print("=" * 60)

    print(f"\nContext: {result.context.description[:100]}...")

    print("\nTerminals:")
    for t in result.terminals:
        print(f"  {t.name} (weight={t.weight:.2f})")

    print("\n" + "-" * 60)
    print(f"{'Rank':<6} {'Option':<20} {'Backward':<10} {'Forward':<10} {'Total':<10}")
    print("-" * 60)

    for rank, option_id in enumerate(result.ranked_options, 1):
        eval_result = result.get_evaluation(option_id)
        if eval_result:
            status = " [ELIMINATED]" if eval_result.eliminated else ""
            print(
                f"{rank:<6} {eval_result.option_name:<20} "
                f"{eval_result.weighted_backward_score:<10.2f} "
                f"{eval_result.forward_score:<10.2f} "
                f"{eval_result.total_score:<10.2f}{status}"
            )

    insights = get_ranking_insights(result.evaluations)
    print(f"\nStatus: {insights.get('message', 'N/A')}")
    print("=" * 60)


def print_results_json(result: DecisionLoopResult):
    """Print results in JSON format."""
    output = {
        "loop_iteration": result.loop_iteration,
        "run_timestamp": result.run_timestamp.isoformat(),
        "context": {
            "description": result.context.description,
            "tags": result.context.tags,
        },
        "terminals": [
            {"id": t.id, "name": t.name, "weight": t.weight}
            for t in result.terminals
        ],
        "rankings": result.ranked_options,
        "evaluations": [
            {
                "option_id": e.option_id,
                "option_name": e.option_name,
                "backward_scores": e.backward_scores,
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
    print(json.dumps(output, indent=2, ensure_ascii=False))


def run_engine(config_path: str, output_format: str = "table", weight_overrides: Optional[dict] = None):
    """Run the decision loop engine with given config."""
    config = load_config(config_path)
    context, terminals, current_state, options = parse_config(config)

    # Apply weight overrides if provided
    if weight_overrides:
        for terminal in terminals:
            if terminal.id in weight_overrides:
                terminal.weight = weight_overrides[terminal.id]

    # Create engine
    engine = DecisionLoopEngine(
        backward_evaluator=AIToolBackwardEvaluator(),
        forward_checker=AIToolForwardChecker()
    )

    # Run
    result = engine.run(context, options, terminals, current_state)

    # Output
    if output_format == "json":
        print_results_json(result)
    elif RICH_AVAILABLE and output_format == "table":
        print_results_rich(result)
    else:
        print_results_plain(result)

    return result


def interactive_mode():
    """Run in interactive mode."""
    if RICH_AVAILABLE:
        console = Console()
        console.print("[bold]Decision Loop Engine - Interactive Mode[/bold]")
    else:
        print("Decision Loop Engine - Interactive Mode")

    # Use default AI tools setup
    context = DecisionContext(
        description="Interactive AI tool selection session",
        tags=["interactive", "ai-tools"],
    )

    terminals = AI_TOOL_TERMINALS.copy()
    options = SAMPLE_AI_TOOLS

    current_state = CurrentState(
        resources={
            "available_hours_per_week": 5,
            "monthly_budget_usd": 30,
            "existing_stack": ["vscode"],
        },
        constraints={
            "must_have_api": False,
            "data_sensitivity": "medium",
            "max_learning_curve": 0.4,
        },
        preferences={
            "risk_tolerance": 0.6,
            "preference_for_new": 0.7,
            "primary_use_case": "coding",
        }
    )

    engine = DecisionLoopEngine(
        backward_evaluator=AIToolBackwardEvaluator(),
        forward_checker=AIToolForwardChecker()
    )

    while True:
        result = engine.run(context, options, terminals, current_state)

        if RICH_AVAILABLE:
            print_results_rich(result)
        else:
            print_results_plain(result)

        print("\nWhat would you like to do?")
        print("  [1] Adjust terminal weights")
        print("  [2] Modify current state")
        print("  [3] View detailed option info")
        print("  [4] Run another loop")
        print("  [5] Export results (JSON)")
        print("  [q] Quit")

        choice = input("\nChoice: ").strip().lower()

        if choice == "q":
            print("Goodbye!")
            break
        elif choice == "1":
            print("\nCurrent weights:")
            for t in terminals:
                print(f"  {t.id}: {t.weight:.2f}")
            print("\nEnter new weights (format: T1_ideal=0.4 T2_realistic=0.4)")
            weights_input = input("Weights: ").strip()
            if weights_input:
                for pair in weights_input.split():
                    if "=" in pair:
                        tid, weight = pair.split("=")
                        for t in terminals:
                            if t.id == tid:
                                t.weight = float(weight)
                                print(f"Updated {tid} to {weight}")
        elif choice == "2":
            print("\nModify current state:")
            print("  [b] Budget")
            print("  [t] Available time")
            print("  [r] Risk tolerance")
            sub = input("Choice: ").strip().lower()
            if sub == "b":
                new_budget = float(input("New monthly budget (USD): "))
                current_state.resources["monthly_budget_usd"] = new_budget
            elif sub == "t":
                new_time = float(input("New available hours per week: "))
                current_state.resources["available_hours_per_week"] = new_time
            elif sub == "r":
                new_risk = float(input("New risk tolerance (0-1): "))
                current_state.preferences["risk_tolerance"] = new_risk
        elif choice == "3":
            print("\nAvailable options:")
            for opt in options:
                print(f"  {opt.id}: {opt.name}")
            opt_id = input("Enter option ID for details: ").strip()
            for opt in options:
                if opt.id == opt_id:
                    print(f"\n{opt.name}")
                    print(f"Description: {opt.description}")
                    print("Features:")
                    for k, v in opt.features.items():
                        print(f"  {k}: {v}")
                    break
        elif choice == "4":
            continue
        elif choice == "5":
            print_results_json(result)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Decision Loop Engine - Structure your decisions with backward and forward thinking"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run decision loop with config file")
    run_parser.add_argument(
        "--config", "-c",
        required=True,
        help="Path to YAML configuration file"
    )
    run_parser.add_argument(
        "--output", "-o",
        choices=["table", "json", "plain"],
        default="table",
        help="Output format (default: table)"
    )
    run_parser.add_argument(
        "--weight", "-w",
        action="append",
        help="Override terminal weight (format: TERMINAL_ID=WEIGHT)"
    )

    # Interactive command
    subparsers.add_parser("interactive", help="Run in interactive mode")

    # Demo command
    subparsers.add_parser("demo", help="Run a quick demo with default settings")

    args = parser.parse_args()

    if args.command == "run":
        weight_overrides = {}
        if args.weight:
            for w in args.weight:
                tid, weight = w.split("=")
                weight_overrides[tid] = float(weight)
        run_engine(args.config, args.output, weight_overrides or None)

    elif args.command == "interactive":
        interactive_mode()

    elif args.command == "demo":
        print("Running demo with default AI tools setup...\n")

        context = DecisionContext(
            description="Demo: Choosing an AI tool for coding and productivity",
            tags=["demo", "ai-tools"],
        )

        current_state = CurrentState(
            resources={
                "available_hours_per_week": 5,
                "monthly_budget_usd": 30,
                "existing_stack": ["vscode", "notion"],
            },
            constraints={
                "must_have_api": False,
                "data_sensitivity": "medium",
                "max_learning_curve": 0.4,
            },
            preferences={
                "risk_tolerance": 0.6,
                "preference_for_new": 0.7,
                "primary_use_case": "coding",
            }
        )

        engine = DecisionLoopEngine(
            backward_evaluator=AIToolBackwardEvaluator(),
            forward_checker=AIToolForwardChecker()
        )

        result = engine.run(context, SAMPLE_AI_TOOLS, AI_TOOL_TERMINALS, current_state)

        if RICH_AVAILABLE:
            print_results_rich(result)
        else:
            print_results_plain(result)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
