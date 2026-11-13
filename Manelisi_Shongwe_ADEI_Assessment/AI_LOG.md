**Tool:** ChatGPT

**Prompt:** Review this SLA calculation: a ticket breaches when its
resolution duration is greater than its category target. What should
happen at 120 minutes and 121 minutes when the target is 120 minutes?

**Output:** The ticket meets the SLA requirement. Its resolution time meets/equals the target. 

**Verification:** I ran the automated checks in `test_sla.py` against
the same `is_breach` function used by the cleaning script. The checks
confirmed that 120 minutes meets a 120-minute target and 121 minutes
breaches it.

**What I adopted:** I used a strict greater-than comparison and kept
both cases as automated regression checks.

**Additional assistance:** ChatGPT helped interpret the brief, inspect
the workbook, draft code and documentation, and troubleshoot setup
and testing. I ran the pipeline locally, checked the reported counts,
and verified the dashboard and its automated checks.