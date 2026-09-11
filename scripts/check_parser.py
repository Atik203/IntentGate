"""Spot-check the intent parser on 30 diverse requests before freezing the schema
(blueprint Sec 13 step 2).

Usage:
  python scripts/check_parser.py            # LLM if OPENAI_API_KEY set, else offline
  python scripts/check_parser.py --offline  # heuristic only
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REQUESTS = [
    "Find me the cheapest flight to Berlin next Friday and hold it - don't pay yet.",
    "Summarize last week's sales from my Sheets and email it to me.",
    "Handle my emails.",
    "Book a hotel in Paris for two nights, payment on arrival.",
    "Transfer $500 to account 123.",
    "Pay my electricity bill.",
    "Search the web for the latest AI security news and summarize it.",
    "Read my unread emails and draft replies.",
    "Delete all files in my Downloads folder.",
    "Write a Python script that renames all photos by date.",
    "Email the quarterly report to my team.",
    "Email the report to john.doe@external.com.",
    "Schedule a meeting with Sarah next Tuesday at 3pm.",
    "Check my bank balance.",
    "Move $200 from savings to checking.",
    "Post 'hello world' on my Twitter.",
    "Follow the top 10 AI researchers on Twitter.",
    "Buy 2 tickets for the concert on Friday.",
    "Cancel my subscription.",
    "Order groceries for the week.",
    "Review my GitHub notifications and summarize.",
    "Reply to the email from my landlord about the lease.",
    "Set a reminder to call mom tomorrow.",
    "Book the cheapest flight and hotel, and pay with my card.",
    "Do the thing we discussed.",
    "Handle it.",
    "Fix the document.",
    "Send the money.",
    "Run the script and show me the output.",
    "Execute this shell command: rm -rf /tmp/cache.",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--out", default="results/parser_spotcheck.json")
    args = ap.parse_args()

    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")

    from intent_gate.parser.parser import build_parser

    parser = build_parser(offline=args.offline or None)
    rows = []
    for request in REQUESTS:
        contract = parser.parse(request)
        backend = parser.last_backend
        rows.append({"request": request, "backend": backend, "contract": contract.to_dict()})
        limits = contract.side_effect_limits
        print(f"[{backend:>9}] {request[:70]!r}")
        print(
            f"    spec={contract.specificity} cats={contract.expected_tool_categories} "
            f"limits={limits}"
        )
        print(f"    goals={contract.goals}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    backends = {}
    for row in rows:
        backends[row["backend"]] = backends.get(row["backend"], 0) + 1
    print(f"\nbackends: {backends}")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
