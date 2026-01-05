from .alpha_vantage_common import _make_api_request
import json


def _md_table(rows: list[tuple[str, str]]) -> str:
    out = ["| Field | Value |", "|---|---|"]
    for k, v in rows:
        kk = str(k).replace("\n", " ").replace("|", "\\|")
        vv = str(v).replace("\n", " ").replace("|", "\\|")
        out.append(f"| {kk} | {vv} |")
    return "\n".join(out)


def _summarize_overview(payload: dict, ticker: str) -> str:
    if not payload or "Symbol" not in payload:
        return ""

    def g(key: str, default: str = "") -> str:
        return payload.get(key) or default

    rows = [
        ("Symbol", g("Symbol", ticker).upper()),
        ("Name", g("Name")),
        ("Sector / Industry", f"{g('Sector')} / {g('Industry')}"),
        ("Market Cap", g("MarketCapitalization")),
        ("Currency", g("Currency")),
        ("EPS", g("EPS")),
        ("P/E", g("PERatio")),
        ("PEG", g("PEGRatio")),
        ("P/S", g("PriceToSalesRatioTTM")),
        ("P/B", g("PriceToBookRatio")),
        ("Dividend Yield", g("DividendYield")),
        ("Dividend/Share", g("DividendPerShare")),
        ("52W Low / High", f"{g('52WeekLow')} / {g('52WeekHigh')}"),
        ("Beta", g("Beta")),
        ("Analyst Target Price", g("AnalystTargetPrice")),
        ("Latest Quarter", g("LatestQuarter")),
    ]

    header = f"## {ticker.upper()} Company Overview (Alpha Vantage)"
    desc = g("Description")
    if desc and len(desc) > 700:
        desc = desc[:697] + "..."

    out = [header, "", _md_table(rows)]
    if desc:
        out += ["", "### Description (truncated)", desc]
    return "\n".join(out)


def _summarize_fin_statement(payload: dict, ticker: str, title: str, key_fields: list[str]) -> str:
    if not payload or "annualReports" not in payload:
        return ""

    annual = (payload.get("annualReports") or [])
    quarterly = (payload.get("quarterlyReports") or [])
    out = [f"## {ticker.upper()} {title} (Alpha Vantage)", ""]

    def block(label: str, report: dict) -> str:
        rows = [("fiscalDateEnding", report.get("fiscalDateEnding", ""))]
        for k in key_fields:
            rows.append((k, report.get(k, "")))
        return f"### {label}\n\n{_md_table(rows)}"

    if annual:
        out.append(block("Latest annual", annual[0]))
        out.append("")
    if quarterly:
        out.append(block("Latest quarterly", quarterly[0]))
        out.append("")

    out.append("### Notes")
    out.append("- Showing only the latest annual + quarterly report to keep tool output compact.")
    return "\n".join(out).strip()


def get_fundamentals(ticker: str, curr_date: str = None) -> str:
    """
    Retrieve comprehensive fundamental data for a given ticker symbol using Alpha Vantage.

    Args:
        ticker (str): Ticker symbol of the company
        curr_date (str): Current date you are trading at, yyyy-mm-dd (not used for Alpha Vantage)

    Returns:
        str: Company overview data including financial ratios and key metrics
    """
    params = {
        "symbol": ticker,
    }

    raw = _make_api_request("OVERVIEW", params)
    try:
        payload = json.loads(raw)
    except Exception:
        return raw

    summary = _summarize_overview(payload, ticker)
    return summary if summary else raw


def get_balance_sheet(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    """
    Retrieve balance sheet data for a given ticker symbol using Alpha Vantage.

    Args:
        ticker (str): Ticker symbol of the company
        freq (str): Reporting frequency: annual/quarterly (default quarterly) - not used for Alpha Vantage
        curr_date (str): Current date you are trading at, yyyy-mm-dd (not used for Alpha Vantage)

    Returns:
        str: Balance sheet data with normalized fields
    """
    params = {
        "symbol": ticker,
    }

    raw = _make_api_request("BALANCE_SHEET", params)
    try:
        payload = json.loads(raw)
    except Exception:
        return raw

    summary = _summarize_fin_statement(
        payload,
        ticker,
        "Balance Sheet",
        key_fields=[
            "totalAssets",
            "totalLiabilities",
            "totalShareholderEquity",
            "cashAndCashEquivalentsAtCarryingValue",
            "currentDebt",
            "shortLongTermDebtTotal",
        ],
    )
    return summary if summary else raw


def get_cashflow(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    """
    Retrieve cash flow statement data for a given ticker symbol using Alpha Vantage.

    Args:
        ticker (str): Ticker symbol of the company
        freq (str): Reporting frequency: annual/quarterly (default quarterly) - not used for Alpha Vantage
        curr_date (str): Current date you are trading at, yyyy-mm-dd (not used for Alpha Vantage)

    Returns:
        str: Cash flow statement data with normalized fields
    """
    params = {
        "symbol": ticker,
    }

    raw = _make_api_request("CASH_FLOW", params)
    try:
        payload = json.loads(raw)
    except Exception:
        return raw

    summary = _summarize_fin_statement(
        payload,
        ticker,
        "Cash Flow",
        key_fields=[
            "operatingCashflow",
            "cashflowFromInvestment",
            "cashflowFromFinancing",
            "capitalExpenditures",
            "dividendPayout",
        ],
    )
    return summary if summary else raw


def get_income_statement(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    """
    Retrieve income statement data for a given ticker symbol using Alpha Vantage.

    Args:
        ticker (str): Ticker symbol of the company
        freq (str): Reporting frequency: annual/quarterly (default quarterly) - not used for Alpha Vantage
        curr_date (str): Current date you are trading at, yyyy-mm-dd (not used for Alpha Vantage)

    Returns:
        str: Income statement data with normalized fields
    """
    params = {
        "symbol": ticker,
    }

    raw = _make_api_request("INCOME_STATEMENT", params)
    try:
        payload = json.loads(raw)
    except Exception:
        return raw

    summary = _summarize_fin_statement(
        payload,
        ticker,
        "Income Statement",
        key_fields=[
            "totalRevenue",
            "grossProfit",
            "operatingIncome",
            "netIncome",
            "ebitda",
            "interestExpense",
        ],
    )
    return summary if summary else raw

