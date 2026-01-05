from openai import OpenAI
from .config import get_config


def _extract_output_text(response) -> str:
    """Best-effort extraction of plain text from an OpenAI Responses API result."""
    # Newer SDKs provide output_text
    text = getattr(response, "output_text", None)
    if isinstance(text, str) and text.strip():
        return text

    # Fallback: try to traverse response.output structure
    output = getattr(response, "output", None)
    if not output:
        return ""
    try:
        chunks = []
        for item in output:
            content = getattr(item, "content", None)
            if not content:
                continue
            for c in content:
                if getattr(c, "type", None) in ("output_text", "text"):
                    t = getattr(c, "text", None)
                    if t:
                        chunks.append(t)
        return "\n".join(chunks).strip()
    except Exception:
        return ""


def _responses_create_with_web_search(client: OpenAI, *, model: str, prompt: str, max_output_tokens: int = 4096):
    """
    Create a Responses request using web search.
    Tries the newer 'web_search' tool first, falls back to 'web_search_preview' for older backends.
    """
    base_kwargs = dict(
        model=model,
        input=[
            {
                "role": "system",
                "content": [{"type": "input_text", "text": prompt}],
            }
        ],
        text={"format": {"type": "text"}},
        temperature=1,
        max_output_tokens=max_output_tokens,
        top_p=1,
        # Avoid persisting user prompts by default.
        store=False,
    )

    try:
        return client.responses.create(
            **base_kwargs,
            tools=[
                {
                    "type": "web_search",
                    "user_location": {"type": "approximate"},
                    "search_context_size": "low",
                }
            ],
        )
    except Exception:
        # Compatibility fallback for older tool name
        return client.responses.create(
            **base_kwargs,
            tools=[
                {
                    "type": "web_search_preview",
                    "user_location": {"type": "approximate"},
                    "search_context_size": "low",
                }
            ],
        )


def get_stock_news_openai(query, start_date, end_date):
    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    prompt = (
        f"Search the web for relevant news and social discussion about {query} "
        f"from {start_date} to {end_date}. Only include items posted in that window."
    )
    response = _responses_create_with_web_search(
        client, model=config["quick_think_llm"], prompt=prompt
    )
    return _extract_output_text(response)


def get_global_news_openai(curr_date, look_back_days=7, limit=5):
    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    prompt = (
        f"Search for global macroeconomics news from {look_back_days} days before {curr_date} "
        f"to {curr_date} that would be informative for trading purposes. "
        f"Only include items posted in that window. Limit to {limit} items."
    )
    response = _responses_create_with_web_search(
        client, model=config["quick_think_llm"], prompt=prompt
    )
    return _extract_output_text(response)


def get_fundamentals_openai(ticker, curr_date):
    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    prompt = (
        f"Search for fundamentals discussions on {ticker} from one month before {curr_date} "
        f"through the month of {curr_date}. Only include items posted in that window. "
        f"Summarize key valuation metrics (P/E, P/S, cash flow, etc.) in a table."
    )
    response = _responses_create_with_web_search(
        client, model=config["quick_think_llm"], prompt=prompt
    )
    return _extract_output_text(response)