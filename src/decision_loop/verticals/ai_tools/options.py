"""
Sample AI Tool Options

Pre-defined options for the AI tool selection vertical.
These represent common AI tools available as of early 2025.
"""

from decision_loop.core.models import Option


SAMPLE_AI_TOOLS = [
    Option(
        id="claude",
        name="Claude (Anthropic)",
        description="Anthropic's conversational AI. Strong in long context, analysis, and coding.",
        features={
            # Core capabilities
            "capability_breadth": 0.85,
            "capability_depth": 0.8,
            "code_generation": 0.85,
            "reasoning": 0.9,
            "creativity": 0.8,
            "multimodal": 0.7,
            # Ecosystem/extensibility
            "ecosystem_size": 0.6,
            "api_availability": True,
            "customization": 0.7,
            "integration_flexibility": 0.75,
            # Learning/accessibility
            "learning_curve": 0.8,  # Easy
            "documentation_quality": 0.85,
            "community_support": 0.7,
            # Cost
            "cost_model": "freemium",
            "monthly_cost_usd": 20,
            "has_free_tier": True,
            # Risk
            "vendor_stability": 0.85,
            "data_privacy": 0.8,
            "lock_in_risk": 0.7,
            # Current state
            "maturity": 0.8,
            "update_frequency": "weekly",
            "momentum": 0.9,
        }
    ),
    Option(
        id="chatgpt",
        name="ChatGPT (OpenAI)",
        description="OpenAI's conversational AI. Largest user base, plugin ecosystem.",
        features={
            "capability_breadth": 0.9,
            "capability_depth": 0.75,
            "code_generation": 0.8,
            "reasoning": 0.8,
            "creativity": 0.85,
            "multimodal": 0.85,
            "ecosystem_size": 0.95,
            "api_availability": True,
            "customization": 0.8,
            "integration_flexibility": 0.85,
            "learning_curve": 0.85,
            "documentation_quality": 0.8,
            "community_support": 0.95,
            "cost_model": "freemium",
            "monthly_cost_usd": 20,
            "has_free_tier": True,
            "vendor_stability": 0.9,
            "data_privacy": 0.6,
            "lock_in_risk": 0.6,
            "maturity": 0.9,
            "update_frequency": "weekly",
            "momentum": 0.85,
        }
    ),
    Option(
        id="cursor",
        name="Cursor",
        description="AI-first code editor. VS Code based, coding specialized.",
        features={
            "capability_breadth": 0.4,  # Coding specialized
            "capability_depth": 0.9,
            "code_generation": 0.95,
            "reasoning": 0.7,
            "creativity": 0.3,
            "multimodal": 0.3,
            "ecosystem_size": 0.7,  # VS Code extension compatible
            "api_availability": False,
            "customization": 0.8,
            "integration_flexibility": 0.6,
            "learning_curve": 0.7,
            "documentation_quality": 0.7,
            "community_support": 0.75,
            "cost_model": "freemium",
            "monthly_cost_usd": 20,
            "has_free_tier": True,
            "vendor_stability": 0.6,
            "data_privacy": 0.5,
            "lock_in_risk": 0.5,
            "maturity": 0.6,
            "update_frequency": "weekly",
            "momentum": 0.95,
        }
    ),
    Option(
        id="gemini",
        name="Gemini (Google)",
        description="Google's AI. Google ecosystem integration, multimodal strength.",
        features={
            "capability_breadth": 0.85,
            "capability_depth": 0.7,
            "code_generation": 0.75,
            "reasoning": 0.75,
            "creativity": 0.7,
            "multimodal": 0.95,
            "ecosystem_size": 0.8,
            "api_availability": True,
            "customization": 0.6,
            "integration_flexibility": 0.9,  # With Google services
            "learning_curve": 0.8,
            "documentation_quality": 0.75,
            "community_support": 0.7,
            "cost_model": "freemium",
            "monthly_cost_usd": 20,
            "has_free_tier": True,
            "vendor_stability": 0.95,
            "data_privacy": 0.5,
            "lock_in_risk": 0.4,
            "maturity": 0.7,
            "update_frequency": "monthly",
            "momentum": 0.8,
        }
    ),
    Option(
        id="perplexity",
        name="Perplexity",
        description="Search + AI. Real-time information access, source citations.",
        features={
            "capability_breadth": 0.6,
            "capability_depth": 0.7,
            "code_generation": 0.5,
            "reasoning": 0.7,
            "creativity": 0.4,
            "multimodal": 0.5,
            "ecosystem_size": 0.3,
            "api_availability": True,
            "customization": 0.3,
            "integration_flexibility": 0.4,
            "learning_curve": 0.9,  # Very easy
            "documentation_quality": 0.6,
            "community_support": 0.5,
            "cost_model": "freemium",
            "monthly_cost_usd": 20,
            "has_free_tier": True,
            "vendor_stability": 0.6,
            "data_privacy": 0.6,
            "lock_in_risk": 0.8,
            "maturity": 0.6,
            "update_frequency": "weekly",
            "momentum": 0.85,
        }
    ),
    Option(
        id="copilot",
        name="GitHub Copilot",
        description="GitHub's AI coding assistant. Deep IDE integration, code completion focus.",
        features={
            "capability_breadth": 0.35,  # Very coding focused
            "capability_depth": 0.85,
            "code_generation": 0.9,
            "reasoning": 0.5,
            "creativity": 0.2,
            "multimodal": 0.1,
            "ecosystem_size": 0.85,  # IDE integrations
            "api_availability": False,
            "customization": 0.6,
            "integration_flexibility": 0.8,
            "learning_curve": 0.85,
            "documentation_quality": 0.8,
            "community_support": 0.85,
            "cost_model": "subscription",
            "monthly_cost_usd": 10,
            "has_free_tier": False,
            "vendor_stability": 0.95,
            "data_privacy": 0.6,
            "lock_in_risk": 0.7,
            "maturity": 0.85,
            "update_frequency": "monthly",
            "momentum": 0.7,
        }
    ),
    Option(
        id="cline",
        name="Cline",
        description="Open-source AI coding agent. VS Code extension, autonomous coding.",
        features={
            "capability_breadth": 0.3,
            "capability_depth": 0.8,
            "code_generation": 0.85,
            "reasoning": 0.65,
            "creativity": 0.2,
            "multimodal": 0.3,
            "ecosystem_size": 0.4,
            "api_availability": False,
            "customization": 0.9,  # Open source
            "integration_flexibility": 0.6,
            "learning_curve": 0.6,
            "documentation_quality": 0.6,
            "community_support": 0.7,
            "cost_model": "free",  # Uses your own API keys
            "monthly_cost_usd": 0,
            "has_free_tier": True,
            "vendor_stability": 0.5,
            "data_privacy": 0.9,  # Self-hosted option
            "lock_in_risk": 0.9,  # Open source
            "maturity": 0.5,
            "update_frequency": "weekly",
            "momentum": 0.8,
        }
    ),
    Option(
        id="windsurf",
        name="Windsurf (Codeium)",
        description="Codeium's AI IDE. Full IDE experience, AI-native design.",
        features={
            "capability_breadth": 0.4,
            "capability_depth": 0.85,
            "code_generation": 0.9,
            "reasoning": 0.7,
            "creativity": 0.3,
            "multimodal": 0.4,
            "ecosystem_size": 0.5,
            "api_availability": False,
            "customization": 0.7,
            "integration_flexibility": 0.5,
            "learning_curve": 0.65,
            "documentation_quality": 0.65,
            "community_support": 0.6,
            "cost_model": "freemium",
            "monthly_cost_usd": 15,
            "has_free_tier": True,
            "vendor_stability": 0.6,
            "data_privacy": 0.6,
            "lock_in_risk": 0.5,
            "maturity": 0.55,
            "update_frequency": "weekly",
            "momentum": 0.9,
        }
    ),
]


def get_option_by_id(option_id: str) -> Option | None:
    """Get an option by its ID."""
    for option in SAMPLE_AI_TOOLS:
        if option.id == option_id:
            return option
    return None


def get_all_option_ids() -> list[str]:
    """Get all available option IDs."""
    return [o.id for o in SAMPLE_AI_TOOLS]
