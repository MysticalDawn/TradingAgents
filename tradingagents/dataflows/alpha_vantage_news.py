from .alpha_vantage_common import _make_api_request, format_datetime_for_api
import json


def _summarize_news_sentiment(payload: dict, *, ticker: str, start_date: str, end_date: str) -> str:
    """
    Convert Alpha Vantage NEWS_SENTIMENT payload into a compact markdown summary.
    This drastically improves LLM usefulness vs raw JSON.
    """
    feed = payload.get("feed") or []
    if not feed:
        return ""

    # Deduplicate by URL
    seen = set()
    rows = []
    for item in feed:
        url = (item.get("url") or item.get("link") or "").strip()
        if url and url in seen:
            continue
        if url:
            seen.add(url)

        title = (item.get("title") or "").strip()
        source = (item.get("source") or "").strip()
        published = (item.get("time_published") or "").strip()
        summary = (item.get("summary") or "").strip()

        # Prefer the ticker-specific sentiment if present
        ticker_sentiment = ""
        tlist = item.get("ticker_sentiment") or []
        if isinstance(tlist, list):
            for ts in tlist:
                if str(ts.get("ticker", "")).upper() == str(ticker).upper():
                    score = ts.get("ticker_sentiment_score")
                    label = ts.get("ticker_sentiment_label")
                    rel = ts.get("relevance_score")
                    ticker_sentiment = f"{label} ({score}), rel={rel}"
                    break

        if not ticker_sentiment:
            overall = item.get("overall_sentiment_label")
            score = item.get("overall_sentiment_score")
            ticker_sentiment = f"{overall} ({score})"

        # Keep summaries short to preserve context window
        if len(summary) > 280:
            summary = summary[:277] + "..."

        rows.append((published, title, source, ticker_sentiment, url, summary))

    # Already sorted by LATEST, but keep stable ordering by published descending
    rows.sort(key=lambda r: r[0], reverse=True)
    rows = rows[:25]

    out = []
    out.append(f"## {ticker.upper()} News & Sentiment (Alpha Vantage) — {start_date} to {end_date}")
    out.append("")
    out.append(
        "| Published | Title | Source | Sentiment | Link |"
    )
    out.append("|---|---|---|---|---|")
    for published, title, source, sentiment, url, _summary in rows:
        safe_title = title.replace("\n", " ").replace("|", "\\|")
        safe_source = source.replace("\n", " ").replace("|", "\\|")
        safe_sent = str(sentiment).replace("\n", " ").replace("|", "\\|")
        link = url if url else ""
        out.append(f"| {published} | {safe_title} | {safe_source} | {safe_sent} | {link} |")

    out.append("")
    out.append("### Notes")
    out.append("- Sentiment uses Alpha Vantage labels/scores; relevance shown when available.")
    out.append("- Summaries are truncated to keep context compact.")

    # Add brief bullets of the top few summaries (more LLM-friendly than a giant blob)
    out.append("")
    out.append("### Top summaries (truncated)")
    for published, title, source, sentiment, url, summary in rows[:8]:
        out.append(f"- **{title}** ({source}, {published}; {sentiment})")
        if url:
            out.append(f"  - Link: {url}")
        if summary:
            out.append(f"  - {summary}")

    return "\n".join(out)

def get_news(ticker, start_date, end_date) -> dict[str, str] | str:
    """Returns live and historical market news & sentiment data from premier news outlets worldwide.

    Covers stocks, cryptocurrencies, forex, and topics like fiscal policy, mergers & acquisitions, IPOs.

    Args:
        ticker: Stock symbol for news articles.
        start_date: Start date for news search.
        end_date: End date for news search.

    Returns:
        Dictionary containing news sentiment data or JSON string.
    """

    params = {
        "tickers": ticker,
        "time_from": format_datetime_for_api(start_date),
        "time_to": format_datetime_for_api(end_date),
        "sort": "LATEST",
        "limit": "50",
    }
    
    raw = _make_api_request("NEWS_SENTIMENT", params)
    try:
        payload = json.loads(raw)
    except Exception:
        # If AV returns non-JSON unexpectedly, keep raw
        return raw

    summary = _summarize_news_sentiment(payload, ticker=ticker, start_date=start_date, end_date=end_date)
    return summary if summary else raw

def get_insider_transactions(symbol: str) -> dict[str, str] | str:
    """Returns latest and historical insider transactions by key stakeholders.

    Covers transactions by founders, executives, board members, etc.

    Args:
        symbol: Ticker symbol. Example: "IBM".

    Returns:
        Dictionary containing insider transaction data or JSON string.
    """

    params = {
        "symbol": symbol,
    }

    return _make_api_request("INSIDER_TRANSACTIONS", params)