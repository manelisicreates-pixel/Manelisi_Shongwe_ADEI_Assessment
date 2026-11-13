# Data cleaning approach

The Tickets_Raw sheet contains 146 data rows, excluding the header.

| Ticket ID | Findings | Cleaning decision |
|---|---|---|
| TK-1038 | Two rows match in every field. | Keep one row and remove the extra copy. |
| TK-1111 | Both rows agree on the opening time, channel and category. One is Open and the other is Resolved with a resolution timestamp. | Count one ticket in volume. Flag the status conflict and exclude the ticket from median resolution time and the SLA denominator because its current status is not verified. |

Row reconciliation before the reporting window: 146 raw rows − 1 blank ID − 2 unusable opening dates − 2 extra rows for repeated IDs = 141 unique tickets. One of the 141 has a status conflict.

Label standardization changed 4 channel values, 3 category values and 3 status values. WA was grouped with WhatsApp, SMS remained a separate channel, and missing labels became Unknowns.

Out of the 141 retained tickets, 94 had valid resolution durations. Three tickets marked Resolved had invalid durations and were excluded from the median and SLA calculation. One valid duration had no matching category target and was included in the median only. Of the 93 SLA-eligible tickets, 46 breached their target.

Among the 141 retained tickets, 69 had valid satisfaction scores, 70 had blank scores, and another 2 with invalid scores were converted to missing. Satisfaction scores did not affect ticket volume, resolution time, or SLA eligibility.

