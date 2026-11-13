from openpyxl import load_workbook

workbook = load_workbook("ADEI_Assessment_Data.xlsx", data_only=True)
tickets = workbook["Tickets_Raw"]

rows = list(tickets.values)
header = rows[0]
ticket_rows = rows[1:]

print("Columns:", ", ".join(header))
print("Raw ticket rows:", len(ticket_rows))

ticket_groups = {}

for row in ticket_rows:
    ticket_id = row[0]
    if ticket_id is None:
        continue

    ticket_id = str(ticket_id).strip()
    ticket_groups.setdefault(ticket_id, []).append(row)

for ticket_id, group in ticket_groups.items():
    if len(group) > 1:
        print(f"\nRepeated ID: {ticket_id}")
        for row in group:
            print(dict(zip(header, row)))