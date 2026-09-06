from datetime import datetime, timedelta, date
from typing import List


def _get_week_start() -> date:
    """Returns this week's Monday."""
    today = date.today()
    return today - timedelta(days=today.weekday())


def _escape_ics_text(text: str) -> str:
    """Escapes characters that have special meaning in the .ics format."""
    return (
        text.replace("\\", "\\\\")
        .replace(",", "\\,")
        .replace(";", "\\;")
        .replace("\n", "\\n")
    )


def build_ics_content(tasks: List[dict]) -> str:
    """Turns a list of task dicts (id, agent, title, hours) into a valid
    .ics calendar file. Tasks are spread round-robin across the 7 days of
    the current week, each starting at 6 PM for its allocated hours."""
    week_start = _get_week_start()
    now_stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//CareerForge//Weekly Plan//EN",
        "CALSCALE:GREGORIAN",
    ]

    for index, task in enumerate(tasks):
        day_offset = index % 7
        event_date = week_start + timedelta(days=day_offset)
        start_dt = datetime.combine(event_date, datetime.min.time()) + timedelta(hours=18)
        end_dt = start_dt + timedelta(hours=task["hours"])

        summary = _escape_ics_text(task["title"])
        agent_label = task["agent"].replace("_", " ").title()
        description = _escape_ics_text(f"CareerForge task - {agent_label} ({task['hours']}h)")

        lines += [
            "BEGIN:VEVENT",
            f"UID:{task['id']}-{now_stamp}@careerforge",
            f"DTSTAMP:{now_stamp}",
            f"DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            "END:VEVENT",
        ]

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)