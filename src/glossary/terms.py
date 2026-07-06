"""
Step 11 — Financial Literacy Layer (Learn tab only).

Static glossary — not connected to the RAG Q&A pipeline.
Use the Learn tab in the app to browse term definitions.
"""

FINANCIAL_TERMS: dict[str, str] = {
    "EBITDA": (
        "EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization) "
        "measures how much money a company earns from its core business operations "
        "before accounting for interest, taxes, and non-cash charges like depreciation. "
        "Think of it as: \"How much cash-like profit did the business generate?\" "
        "It helps compare operating performance across companies without the noise "
        "of financing decisions or tax rules."
    ),
    "EPS": (
        "Earnings Per Share (EPS) is the company's net profit divided by the number "
        "of outstanding shares. If a company earned ₹100 crore and has 10 crore shares, "
        "EPS is ₹10 per share. It shows how much profit each share earned — useful "
        "when comparing companies of different sizes."
    ),
    "ROE": (
        "Return on Equity (ROE) shows how efficiently a company uses shareholders' money. "
        "It is net profit divided by shareholders' equity, expressed as a percentage. "
        "A higher ROE generally means the company is generating more profit from "
        "each rupee of investor capital."
    ),
    "Revenue": (
        "Revenue is the total money a company earns from selling its goods or services "
        "before subtracting any costs. It is also called sales or turnover. "
        "Revenue growth tells you whether the business is getting bigger."
    ),
    "Profit": (
        "Profit (or net income) is what remains after subtracting all expenses — "
        "including salaries, raw materials, taxes, and interest — from revenue. "
        "A company can have high revenue but low profit if costs are too high."
    ),
    "Debt": (
        "Debt is money the company has borrowed and must repay, usually with interest. "
        "Some debt is normal for growth, but too much debt can be risky if profits fall "
        "and the company struggles to make repayments."
    ),
    "Assets": (
        "Assets are everything the company owns that has value — cash, buildings, "
        "equipment, inventory, and investments. Assets are listed on the balance sheet "
        "and are used to generate revenue."
    ),
    "Cash Flow": (
        "Cash flow is the actual movement of money in and out of a business. "
        "A company can show a profit on paper but still run out of cash if customers "
        "pay late or if it spends heavily on equipment. Positive cash flow means "
        "more money is coming in than going out."
    ),
}


def explain_term(term: str) -> str:
    """
    Return a layman-friendly explanation for a financial term.

    Args:
        term: Term to explain (e.g. "EBITDA").

    Returns:
        Explanation string, or a not-found message.
    """
    if not term or not term.strip():
        return ""

    normalized = term.strip()
    if normalized in FINANCIAL_TERMS:
        return FINANCIAL_TERMS[normalized]

    for key, definition in FINANCIAL_TERMS.items():
        if key.lower() == normalized.lower():
            return definition

    return (
        f"I don't have a definition for '{term}' yet. "
        "Try EBITDA, EPS, ROE, Revenue, or Profit."
    )


def get_learn_topics() -> list[str]:
    """Return sorted list of glossary terms for the Learn tab."""
    return sorted(FINANCIAL_TERMS.keys())
