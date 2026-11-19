"""Checks for the birthdays and messages in town.json and in the network
settings file. The JSON schemas check the format of the dates; these
functions check that the dates exist on a calendar. This file uses only the
Python standard library, so tools/check_external_config.py can use it on a
computer that does not have the generator's other packages."""

import datetime

def date_problems(data):
    """Returns a list of problems with the dates in data["birthdays"] and
    data["messages"], each one naming the entry. The format is checked by
    the schema first, so only well-formed values are checked here."""
    problems = []
    for i, b in enumerate(data.get("birthdays", []) or []):
        date = b.get("date", "") if isinstance(b, dict) else ""
        try:
            # 2024 has February 29, so "02-29" is allowed
            datetime.date.fromisoformat("2024-" + date)
        except ValueError:
            problems.append(f'birthdays/{i}: "{date}" is not a day of the year. Use month and day, for example "11-20".')
    for i, m in enumerate(data.get("messages", []) or []):
        if not isinstance(m, dict):
            continue
        days = {}
        for key in ("from", "until"):
            if key in m:
                try:
                    days[key] = datetime.date.fromisoformat(m[key])
                except (TypeError, ValueError):
                    problems.append(f'messages/{i}/{key}: "{m[key]}" is not a date. Use year, month, and day, for example "2026-11-26".')
        if "from" in days and "until" in days and days["from"] > days["until"]:
            problems.append(f"messages/{i}: from ({m['from']}) is after until ({m['until']}), so the text never shows.")
    return problems

def fill(data):
    """The birthdays and messages from data, with "where" filled in."""
    birthdays = [dict({"where": "both"}, **b) for b in data.get("birthdays", [])]
    messages = [dict({"where": "both"}, **m) for m in data.get("messages", [])]
    return birthdays, messages
