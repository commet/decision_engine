# Decision Loop Engine

A decision-structuring engine that combines backward induction and forward feasibility checks to help structure complex decisions across multiple possible futures.

## What This Is

This is **not** a recommendation system or optimizer.

This is a tool for:
1. Making implicit human judgment explicit
2. Combining backward (future-fit) and forward (feasibility) thinking
3. Allowing iterative correction over time
4. Showing its work transparently

## Core Concepts

### Multiple Terminals, Not One Goal

The engine doesn't assume a single goal. Instead, you define **multiple terminal states** representing different judgment criteria:

| Terminal | Purpose |
|----------|---------|
| **Ideal** | Best-case future if everything goes well |
| **Realistic** | Most likely achievable future |
| **Regret-Minimized** | Avoiding worst outcomes |

### Backward Induction

Answers: "If I want to reach this Terminal, what conditions must my choice satisfy?"

### Forward Sanity Check

Answers: "Given my current state (time, budget, constraints), can I actually execute this choice?"

### Loop Structure

```
Decision → Execution → Feedback → Terminal Adjustment → Weight Modification → Option Redefinition → (Repeat)
```

## Installation

```bash
pip install -e .
```

## Quick Start

### Demo Mode

```bash
decision-loop demo
```

### With Configuration File

```bash
decision-loop run --config configs/ai_tools_example.yaml
```

### Interactive Mode

```bash
decision-loop interactive
```

### JSON Output

```bash
decision-loop run --config configs/ai_tools_example.yaml --output json
```

### Override Terminal Weights

```bash
decision-loop run --config configs/ai_tools_example.yaml --weight T1_ideal=0.5 --weight T2_realistic=0.3
```

## Project Structure

```
decision_engine/
├── src/decision_loop/
│   ├── core/              # Domain-agnostic engine
│   │   ├── models.py      # Data classes
│   │   ├── engine.py      # DecisionLoopEngine
│   │   ├── evaluators.py  # Abstract interfaces
│   │   └── scoring.py     # Score calculations
│   ├── verticals/         # Domain-specific implementations
│   │   └── ai_tools/      # AI Tool Selection vertical
│   └── cli/               # Command-line interface
├── configs/               # Example configurations
└── tests/                 # Test suite
```

## First Vertical: AI Tool Selection

The first concrete implementation helps with choosing AI tools (Claude, GPT, Cursor, etc.).

### Sample Configuration

```yaml
context:
  description: "Choosing an AI tool for coding and productivity"

terminals:
  - id: T1_ideal
    name: Ideal Future
    weight: 0.3
    criteria:
      min_capability_breadth: 0.8
      min_ecosystem_size: 0.7

  - id: T2_realistic
    name: Realistic Future
    weight: 0.5
    criteria:
      min_learning_curve: 0.5
      max_monthly_cost_usd: 50

  - id: T3_minimum
    name: Regret-Minimized
    weight: 0.2
    criteria:
      min_vendor_stability: 0.8
      has_free_tier: true

current_state:
  resources:
    available_hours_per_week: 5
    monthly_budget_usd: 30
  constraints:
    must_have_api: false
    data_sensitivity: medium
  preferences:
    risk_tolerance: 0.6
    primary_use_case: coding
```

## What This Engine Does NOT Guarantee

1. **Automatic decision-making** - It provides rankings and scores, not commands
2. **"Optimal" choice claims** - Results depend on your settings
3. **Terminal validity checking** - Garbage in, garbage out
4. **Quantifying unquantifiable friction** - Psychology and emotions aren't fully captured
5. **Preventing infinite loops** - Execution without action is your responsibility

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -v
```

## License

MIT
