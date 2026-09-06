# Spot-check intent parser on ~30 diverse requests before freezing schema (blueprint Sec 13 step 2).
from __future__ import annotations

from intent_gate.parser.parser import IntentParser


def main():
    requests = [
        "Find me the cheapest flight to Berlin next Friday and hold it - don't pay yet.",
        "Summarize last week's sales from my Sheets and email it to me.",
        "Handle my emails.",
        "Book a hotel in Paris for two nights.",
        "Transfer $500 to account 123.",
    ]
    parser = IntentParser()
    for req in requests:
        c = parser.parse(req)
        print(f"- {req!r}")
        print(f"  goals={c.goals} cats={c.expected_tool_categories} spec={c.specificity}")
        print(f"  limits={c.side_effect_limits}")


if __name__ == "__main__":
    main()
