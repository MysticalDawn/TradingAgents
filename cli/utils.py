import questionary
from typing import List, Optional, Tuple, Dict

from rich.console import Console

from cli.models import AnalystType

console = Console()

ANALYST_ORDER = [
    ("Market Analyst", AnalystType.MARKET),
    ("Social Media Analyst", AnalystType.SOCIAL),
    ("News Analyst", AnalystType.NEWS),
    ("Fundamentals Analyst", AnalystType.FUNDAMENTALS),
]


def get_ticker() -> str:
    """Prompt the user to enter a ticker symbol."""
    ticker = questionary.text(
        "Enter the ticker symbol to analyze:",
        validate=lambda x: len(x.strip()) > 0 or "Please enter a valid ticker symbol.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not ticker:
        console.print("\n[red]No ticker symbol provided. Exiting...[/red]")
        exit(1)

    return ticker.strip().upper()


def get_analysis_date() -> str:
    """Prompt the user to enter a date in YYYY-MM-DD format."""
    import re
    from datetime import datetime

    def validate_date(date_str: str) -> bool:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    date = questionary.text(
        "Enter the analysis date (YYYY-MM-DD):",
        validate=lambda x: validate_date(x.strip())
        or "Please enter a valid date in YYYY-MM-DD format.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not date:
        console.print("\n[red]No date provided. Exiting...[/red]")
        exit(1)

    return date.strip()


def select_analysts() -> List[AnalystType]:
    """Select analysts using an interactive checkbox."""
    choices = questionary.checkbox(
        "Select Your [Analysts Team]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in ANALYST_ORDER
        ],
        instruction="\n- Press Space to select/unselect analysts\n- Press 'a' to select/unselect all\n- Press Enter when done",
        validate=lambda x: len(x) > 0 or "You must select at least one analyst.",
        style=questionary.Style(
            [
                ("checkbox-selected", "fg:green"),
                ("selected", "fg:green noinherit"),
                ("highlighted", "noinherit"),
                ("pointer", "noinherit"),
            ]
        ),
    ).ask()

    if not choices:
        console.print("\n[red]No analysts selected. Exiting...[/red]")
        exit(1)

    return choices


def select_research_depth() -> int:
    """Select research depth using an interactive selection."""

    # Define research depth options with their corresponding values
    DEPTH_OPTIONS = [
        ("Shallow - Quick research, few debate and strategy discussion rounds", 1),
        ("Medium - Middle ground, moderate debate rounds and strategy discussion", 3),
        ("Deep - Comprehensive research, in depth debate and strategy discussion", 5),
    ]

    choice = questionary.select(
        "Select Your [Research Depth]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in DEPTH_OPTIONS
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:yellow noinherit"),
                ("highlighted", "fg:yellow noinherit"),
                ("pointer", "fg:yellow noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]No research depth selected. Exiting...[/red]")
        exit(1)

    return choice


def select_shallow_thinking_agent(provider: str) -> str:
    """Select shallow thinking llm engine using an interactive selection."""
    provider_key = (provider or "").strip().lower()

    # Define shallow thinking llm engine options with their corresponding model names
    SHALLOW_AGENT_OPTIONS = {
        "openai": [
            ("GPT-4.1 - High quality general model", "gpt-4.1"),
            ("GPT-5-nano - Ultra-fast and ultra-cheap for trivial tasks", "gpt-5-nano"),
            ("GPT-5-mini - Fast general-purpose lightweight model", "gpt-5-mini"),
            (
                "GPT-4.1-nano - Ultra-lightweight model for basic operations",
                "gpt-4.1-nano",
            ),
            ("GPT-4.1-mini - Compact model with good performance", "gpt-4.1-mini"),
            ("GPT-4o-mini - Fast and efficient for quick tasks", "gpt-4o-mini"),
            ("GPT-4o - Standard multimodal model", "gpt-4o"),
            ("o4-mini - Low-cost reasoning model (good default)", "o4-mini"),
        ],
        "anthropic": [
            (
                "Claude Haiku 3.5 - Fast inference and low cost",
                "claude-3-5-haiku-latest",
            ),
            (
                "Claude Sonnet 3.5 - Strong general reasoning",
                "claude-3-5-sonnet-latest",
            ),
            (
                "Claude Sonnet 3.7 - Hybrid reasoning & agentic behavior",
                "claude-3-7-sonnet-latest",
            ),
            ("Claude Sonnet 4 - High performance standard model", "claude-sonnet-4-0"),
        ],
        "google": [
            ("Gemini 2.0 Flash-Lite - Lowest latency & cost", "gemini-2.0-flash-lite"),
            ("Gemini 2.0 Flash - Fast multimodal reasoning", "gemini-2.0-flash"),
            (
                "Gemini 2.5 Flash - Adaptive thinking & efficiency (stable)",
                "gemini-2.5-flash",
            ),
            (
                "Gemini 2.5 Flash - Adaptive thinking & efficiency (preview)",
                "gemini-2.5-flash-preview",
            ),
            (
                "Gemini 3 Flash - Next-gen lightweight reasoning (stable)",
                "gemini-3-flash",
            ),
            (
                "Gemini 3 Flash - Next-gen lightweight reasoning (preview)",
                "gemini-3-flash-preview",
            ),
        ],
        "openrouter": [
            (
                "Meta: Llama 4 Scout - Fast open-weight model",
                "meta-llama/llama-4-scout",
            ),
            ("Meta: Llama 3.3 8B Instruct", "meta-llama/llama-3.3-8b-instruct"),
            ("Meta: Llama 3.3 70B Instruct", "meta-llama/llama-3.3-70b-instruct"),
            ("Google: Gemini 2.0 Flash (exp)", "google/gemini-2.0-flash-exp"),
            ("DeepSeek R1 (reasoning)", "deepseek/deepseek-r1"),
        ],
        "ollama": [
            ("llama3.2 local", "llama3.2"),
            ("llama3.3 local", "llama3.3"),
            ("qwen2.5 local", "qwen2.5"),
        ],
    }

    if provider_key not in SHALLOW_AGENT_OPTIONS:
        console.print(
            f"\n[red]Unsupported LLM provider '{provider}'. Supported: {', '.join(SHALLOW_AGENT_OPTIONS.keys())}[/red]"
        )
        exit(1)

    choice = questionary.select(
        "Select Your [Quick-Thinking LLM Engine]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in SHALLOW_AGENT_OPTIONS[provider_key]
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print(
            "\n[red]No shallow thinking llm engine selected. Exiting...[/red]"
        )
        exit(1)

    return choice


def select_deep_thinking_agent(provider: str) -> str:
    """Select deep thinking llm engine using an interactive selection."""
    provider_key = (provider or "").strip().lower()

    # Define deep thinking llm engine options with their corresponding model names
    DEEP_AGENT_OPTIONS = {
        "openai": [
            ("o4-mini - Low-cost reasoning model (default)", "o4-mini"),
            ("o4 - Higher-end reasoning model", "o4"),
            ("o3-mini - Lightweight advanced reasoning", "o3-mini"),
            ("o3 - Full advanced reasoning model", "o3"),
            ("o1-preview - Legacy reasoning preview model", "o1-preview"),
            ("o1-mini - Lower-cost long-horizon reasoning", "o1-mini"),
            ("o1 - Premier long-horizon reasoning model", "o1"),
            ("o1-pro - Extended context & planning", "o1-pro"),
            ("GPT-5-mini - Strong reasoning at lower cost", "gpt-5-mini"),
            ("GPT-5 - Flagship general intelligence model", "gpt-5"),
        ],
        "anthropic": [
            ("Claude Haiku 3.5 - Fast inference", "claude-3-5-haiku-latest"),
            (
                "Claude Sonnet 3.7 - Hybrid reasoning & tools",
                "claude-3-7-sonnet-latest",
            ),
            ("Claude Sonnet 4 - High reasoning accuracy", "claude-sonnet-4-0"),
            ("Claude Opus 4 - Most powerful Anthropic model", "claude-opus-4-0"),
        ],
        "google": [
            ("Gemini 2.5 Flash - Adaptive thinking (stable)", "gemini-2.5-flash"),
            (
                "Gemini 2.5 Flash - Adaptive thinking (preview)",
                "gemini-2.5-flash-preview",
            ),
            ("Gemini 2.5 Pro - High-end reasoning (stable)", "gemini-2.5-pro"),
            ("Gemini 2.5 Pro - High-end reasoning (preview)", "gemini-2.5-pro-preview"),
            ("Gemini 3 Pro - Frontier reasoning & multimodal (stable)", "gemini-3-pro"),
            (
                "Gemini 3 Pro - Frontier reasoning & multimodal (preview)",
                "gemini-3-pro-preview",
            ),
        ],
        "openrouter": [
            (
                "DeepSeek V3 - 685B MoE flagship reasoning model",
                "deepseek/deepseek-chat-v3",
            ),
            ("DeepSeek R1 - Strong reasoning model", "deepseek/deepseek-r1"),
            (
                "Qwen2.5 72B Instruct - Strong open reasoning",
                "qwen/qwen2.5-72b-instruct",
            ),
            (
                "Meta: Llama 3.3 70B Instruct - Strong general open-weight",
                "meta-llama/llama-3.3-70b-instruct",
            ),
        ],
        "ollama": [
            ("llama3.3 local", "llama3.3"),
            ("qwen2.5 local", "qwen2.5"),
            ("deepseek-r1 local", "deepseek-r1"),
        ],
    }

    if provider_key not in DEEP_AGENT_OPTIONS:
        console.print(
            f"\n[red]Unsupported LLM provider '{provider}'. Supported: {', '.join(DEEP_AGENT_OPTIONS.keys())}[/red]"
        )
        exit(1)

    choice = questionary.select(
        "Select Your [Deep-Thinking LLM Engine]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in DEEP_AGENT_OPTIONS[provider_key]
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]No deep thinking llm engine selected. Exiting...[/red]")
        exit(1)

    return choice


def select_llm_provider() -> tuple[str, str]:
    """Select the OpenAI api url using interactive selection."""
    # Define OpenAI api options with their corresponding endpoints
    BASE_URLS = [
        ("OpenAI", "https://api.openai.com/v1"),
        ("Anthropic", "https://api.anthropic.com/"),
        ("Google", "https://generativelanguage.googleapis.com/v1"),
        ("Openrouter", "https://openrouter.ai/api/v1"),
        ("Ollama", "http://localhost:11434/v1"),
    ]

    choice = questionary.select(
        "Select your LLM Provider:",
        choices=[
            questionary.Choice(display, value=(display, value))
            for display, value in BASE_URLS
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]no OpenAI backend selected. Exiting...[/red]")
        exit(1)

    display_name, url = choice
    print(f"You selected: {display_name}\tURL: {url}")

    return display_name, url
