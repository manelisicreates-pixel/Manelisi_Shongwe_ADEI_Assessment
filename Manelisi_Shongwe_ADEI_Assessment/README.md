#ADEI JUNIOR SOFTWARE ENGINEER TAKE-HOME ASSESSMENT

** Name:** Manelisi Shongwe
** Track:** Software Engineer

##Intention of dashboard 
To support operation lead's decision on which channels and week to investigate first wehn looking for missed resolution targets.

##Findings

The reporting window contained 141 unique tickets. Median resolution time
was 298 minutes across 94 valid durations. 46 of 93 SLA-eligible
tickets (49.5%) breached their category target.

1. Email recorded the most breaches, with 18 of 33 eligible tickets
   (54.5%), compared with Web at 16 of 34 (47.1%) and WhatsApp at
   10 of 24 (41.7%).
2. The week starting 26 October had the highest breach rate, with 18 of
   25 eligible tickets (72.0%) breached. The previous week had 7 breaches among
   21 eligible tickets (33.3%), which would amount to an increase of 38.7%.

##Recommended action

Review the 18 breached tickets opened in the week starting 26 October.
Break them down by channel and category, then investigate the ticket histories
for recurring delays, emails must be included in the review because it accounted
for the most breaches across the entire reporting window.

##Limitation
SMS and Unknown each show a 100% breach rate based on one eligible
ticket. Those rates are to be taken on a case-by-case basis to be able to rank the
channels confidently. The SLA rate also covers only tickets with a valid
resolution duration and a matching target, so unresolved tickets are
outside that measures/parameters.

##Setup and running

Open PowerShell in the project folder. Create the virtual environment,
install dependencies, generate the dashboard data, and start the server.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe clean.py
.\.venv\Scripts\python.exe -m http.server 8000 --directory dashboard
```

Open http://localhost:8000 in a browser.

##Automated checks

In a second PowerShell terminal, run:

```powershell
.\.venv\Scripts\python.exe -m unittest test_sla -v
```

These tests verify that a resolution exactly at the SLA target meets it
and that a resolution one minute over the target breaches it.

With the server running, open http://localhost:8000/test-empty-filter.html.
The page automatically checks that an empty channel selection shows a
message, clears the previous chart and displays SLA as unavailable.

##How the dashboard gets its data

`clean.py` reads the workbook, applies the cleaning and SLA rules, and
writes overall, channel and weekly summaries to `dashboard/data.json`.
`dashboard/app.js` loads that file and updates the metric cards and
weekly chart when the channel changes.

See [CLEANING.md](CLEANING.md) for the row counts and cleaning decisions.