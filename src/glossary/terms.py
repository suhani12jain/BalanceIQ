"""
Step 17 — Financial Literacy Layer.

Explains financial terms in plain language when users ask
(e.g. "What is EBITDA?").
"""

# Static definitions for quick lookup without an API call
FINANCIAL_TERMS: dict[str, str] = {
    "EBITDA": (
        "EBITDA measures how much money the company earns from its core business "
        "before accounting and financing costs. It helps compare operating performance."
    ),
    "EPS": (
        "Earnings Per Share — net profit divided by outstanding shares. "
        "Shows how much profit each share earned."
    ),
    "ROE": (
        "Return on Equity — net income as a percentage of shareholders' equity. "
        "Shows how efficiently the company uses investor money."
    ),
    "Revenue": (
        "Total money earned from selling goods or services before expenses. "
        "Also called turnover or sales."
    ),
    "Profit": (
        "Money left after subtracting all costs from revenue. "
        "Also called net income or earnings."
    ),
    "Debt": (
        "Money borrowed by the company that must be repaid with interest."
    ),
    "Cash Flow": (
        "Actual cash moving in and out of the business. "
        "A company can be profitable but still run out of cash."
    ),
}


def detect_financial_terms(query: str) -> list[str]:
    """
    Identify financial terms mentioned in the user's question.

    Args:
        query: User question text.

    Returns:
        List of detected term keys (e.g. ["EBITDA", "ROE"]).
    """
    # TODO: Case-insensitive match against FINANCIAL_TERMS keys and aliases
    pass


def explain_term(term: str) -> str:
    """
    Return a layman-friendly explanation for a financial term.

    Args:
        term: Term to explain (e.g. "EBITDA").

    Returns:
        Explanation string, or a not-found message.
    """
    # TODO: Lookup in FINANCIAL_TERMS (case-insensitive)
    pass


def explain_terms_in_query(query: str) -> str:
    """
    If the query asks about terminology, return combined explanations.

    Args:
        query: User's natural-language question.

    Returns:
        Formatted glossary text, or empty string if no terms detected.
    """
    # TODO: detect_financial_terms + explain_term for each
    pass


def get_learn_topics() -> list[str]:
    """
    Return list of terms for the "Learn" sidebar (Step 18 UI).

    Returns:
        Sorted list of available glossary terms.
    """
    return sorted(FINANCIAL_TERMS.keys())
