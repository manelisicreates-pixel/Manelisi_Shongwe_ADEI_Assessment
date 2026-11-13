from datetime import datetime, timedelta, timezone

from openpyxl import load_workbook

SAST = timezone(timedelta(hours=2))


def parse_timestamp(value):
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.strip())
        except ValueError:
            return None

    if not isinstance(value, datetime):
        return None

    if value.tzinfo is None:
        return value.replace(tzinfo=SAST)

    return value.astimezone(SAST)


workbook = load_workbook("ADEI_Assessment_Data.xlsx", data_only=True)
header, *raw_rows = workbook["Tickets_Raw"].values

usable_rows = []
missing_ids = 0
invalid_openings = 0

for raw_row in raw_rows:
    ticket = dict(zip(header, raw_row))
    ticket_id = str(ticket["ticket_id"] or "").strip()

    if not ticket_id:
        missing_ids += 1
        continue

    opened_at = parse_timestamp(ticket["opened_at"])
    if opened_at is None:
        invalid_openings += 1
        continue

    ticket["ticket_id"] = ticket_id
    ticket["opened_at"] = opened_at
    usable_rows.append(ticket)

assert len(raw_rows) == missing_ids + invalid_openings + len(usable_rows)

print("Raw ticket rows:", len(raw_rows))
print("Excluded for blank ID:", missing_ids)
print("Excluded for unusable opening date:", invalid_openings)
print("Rows with usable IDs and opening dates:", len(usable_rows))

tickets_by_id = {}

for ticket in usable_rows:
    ticket_id = ticket["ticket_id"]
    tickets_by_id.setdefault(ticket_id, []).append(ticket)

unique_tickets = []
duplicate_rows_removed = 0
status_conflicts = 0

for ticket_id, group in tickets_by_id.items():
    ticket = group[0].copy()
    duplicate_rows_removed += len(group) - 1

    if any(other != ticket for other in group[1:]):
        agreed_fields = ("opened_at", "channel", "category")

        if any(
            other[field] != ticket[field]
            for other in group[1:]
            for field in agreed_fields
        ):
            raise ValueError(f"Review conflicting ticket details for {ticket_id}")

        ticket["status"] = "Conflict"
        ticket["resolved_at"] = None
        ticket["csat"] = None
        status_conflicts += 1

    unique_tickets.append(ticket)

assert len(usable_rows) == len(unique_tickets) + duplicate_rows_removed

print("Extra rows removed for repeated IDs:", duplicate_rows_removed)
print("Conflicting tickets retained for volume only:", status_conflicts)
print("Unique tickets before the reporting window:", len(unique_tickets))

window_start = datetime(2026, 10, 5, tzinfo=SAST)
window_end = datetime(2026, 11, 2, tzinfo=SAST)

in_window_tickets = []

for ticket in unique_tickets:
    opened_at = ticket["opened_at"]

    if window_start <= opened_at < window_end:
        opened_date = opened_at.date()
        days_since_monday = opened_date.weekday()
        ticket["week_start"] = opened_date - timedelta(days=days_since_monday)
        in_window_tickets.append(ticket)

outside_window = len(unique_tickets) - len(in_window_tickets)

assert all(
    window_start <= ticket["opened_at"] < window_end
    for ticket in in_window_tickets
)
assert len({ticket["ticket_id"] for ticket in in_window_tickets}) == len(in_window_tickets)

print("Excluded outside reporting window:", outside_window)
print("Final unique tickets in reporting window:", len(in_window_tickets))

from collections import Counter


def clean_label(value):
    return str(value or "").strip().title() or "Unknown"


channel_names = {
    "Wa": "WhatsApp",
    "Whatsapp": "WhatsApp",
    "Sms": "SMS",
}

label_changes = Counter()

for ticket in in_window_tickets:
    for field in ("channel", "category", "status"):
        original = ticket[field]
        cleaned = clean_label(original)

        if field == "channel":
            cleaned = channel_names.get(cleaned, cleaned)

        if original != cleaned:
            label_changes[field] += 1

        ticket[field] = cleaned

channel_counts = Counter(ticket["channel"] for ticket in in_window_tickets)

print("\nLabel changes:")
for field in ("channel", "category", "status"):
    print(f"  {field}: {label_changes[field]}")

print("\nTickets by channel:")
for channel, count in sorted(channel_counts.items()):
    print(f"  {channel}: {count}")

assert sum(channel_counts.values()) == len(in_window_tickets)

sla_targets = {}

for category, target_minutes in list(workbook["SLA_Rules"].values)[1:]:
    sla_targets[clean_label(category)] = target_minutes


def is_breach(duration_minutes, target_minutes):
    return duration_minutes > target_minutes


valid_durations = 0
invalid_durations = 0
missing_targets = 0
sla_eligible = 0
sla_breaches = 0

for ticket in in_window_tickets:
    ticket["resolution_minutes"] = None
    ticket["sla_breach"] = None

    if ticket["status"] != "Resolved":
        continue

    resolved_at = parse_timestamp(ticket["resolved_at"])
    if resolved_at is None or resolved_at < ticket["opened_at"]:
        invalid_durations += 1
        continue

    elapsed = resolved_at - ticket["opened_at"]
    minutes = elapsed.total_seconds() / 60
    ticket["resolution_minutes"] = minutes
    valid_durations += 1

    target = sla_targets.get(ticket["category"])
    if target is None:
        missing_targets += 1
        continue

    ticket["sla_breach"] = is_breach(minutes, target)
    sla_eligible += 1
    if ticket["sla_breach"]:
        sla_breaches += 1

assert valid_durations == sla_eligible + missing_targets
assert 0 <= sla_breaches <= sla_eligible

print("\nResolution and SLA:")
print("  Valid resolution durations:", valid_durations)
print("  Resolved tickets with invalid durations:", invalid_durations)
print("  Valid durations with no matching SLA target:", missing_targets)
print("  SLA-eligible tickets:", sla_eligible)
print("  SLA breaches:", sla_breaches)

valid_csat = 0
missing_csat = 0
invalid_csat = 0

for ticket in in_window_tickets:
    score = str(ticket["csat"] if ticket["csat"] is not None else "").strip()

    if score == "":
        ticket["csat"] = None
        missing_csat += 1
    elif score in {"1", "2", "3", "4", "5"}:
        ticket["csat"] = int(score)
        valid_csat += 1
    else:
        ticket["csat"] = None
        invalid_csat += 1

assert valid_csat + missing_csat + invalid_csat == len(in_window_tickets)

print("\nCustomer satisfaction (CSAT):")
print("  Valid scores:", valid_csat)
print("  Missing scores:", missing_csat)
print("  Invalid scores converted to missing:", invalid_csat)

from statistics import median


def summarize(tickets):
    durations = [
        ticket["resolution_minutes"]
        for ticket in tickets
        if ticket["resolution_minutes"] is not None
    ]
    sla_results = [
        ticket["sla_breach"]
        for ticket in tickets
        if ticket["sla_breach"] is not None
    ]
    breaches = sla_results.count(True)

    return {
        "volume": len(tickets),
        "resolution_count": len(durations),
        "median_minutes": median(durations) if durations else None,
        "sla_eligible": len(sla_results),
        "sla_breaches": breaches,
        "sla_rate": breaches / len(sla_results) if sla_results else None,
    }


def print_metrics(label, metrics):
    median_minutes = metrics["median_minutes"]
    median_text = "N/A" if median_minutes is None else f"{median_minutes:g} min"

    rate = metrics["sla_rate"]
    rate_text = "N/A" if rate is None else f"{rate:.1%}"

    print(
        f"{label} | {metrics['volume']} tickets | "
        f"Median {median_text} ({metrics['resolution_count']} durations) | "
        f"SLA breach rate {rate_text} "
        f"({metrics['sla_breaches']} of {metrics['sla_eligible']} eligible)"
    )


overall = summarize(in_window_tickets)
print("\nOverall:")
print_metrics("All channels", overall)

print("\nBy channel:")
for channel in sorted(channel_counts):
    channel_tickets = [
        ticket for ticket in in_window_tickets if ticket["channel"] == channel
    ]
    print_metrics(channel, summarize(channel_tickets))

print("\nBy week (Monday start):")
for week_number in range(4):
    monday = window_start.date() + timedelta(weeks=week_number)
    week_tickets = [
        ticket for ticket in in_window_tickets if ticket["week_start"] == monday
    ]
    print_metrics(monday.isoformat(), summarize(week_tickets))

    import json
from pathlib import Path


def summarize_weeks(tickets):
    weeks = []

    for week_number in range(4):
        monday = window_start.date() + timedelta(weeks=week_number)
        week_tickets = [
            ticket for ticket in tickets if ticket["week_start"] == monday
        ]
        weeks.append({
            "week_start": monday.isoformat(),
            **summarize(week_tickets),
        })

    return weeks


dashboard_data = {
    "overall": summarize(in_window_tickets),
    "weeks": summarize_weeks(in_window_tickets),
    "channels": {},
}

for channel in sorted(channel_counts):
    channel_tickets = [
        ticket for ticket in in_window_tickets if ticket["channel"] == channel
    ]
    dashboard_data["channels"][channel] = {
        "overall": summarize(channel_tickets),
        "weeks": summarize_weeks(channel_tickets),
    }

output_file = Path("dashboard") / "data.json"
output_file.parent.mkdir(exist_ok=True)
output_file.write_text(json.dumps(dashboard_data, indent=2), encoding="utf-8")

print("\nDashboard data saved to dashboard/data.json")