const channelSelect = document.querySelector("#channel");
const statusMessage = document.querySelector("#status");
const metrics = document.querySelector("#metrics");
const trend = document.querySelector("#trend");

function formatRate(rate) {
  return rate === null ? "N/A" : `${(rate * 100).toFixed(1)}%`;
}

function renderDashboard(summary) {
  metrics.replaceChildren();
  trend.replaceChildren();

  if (!summary || summary.overall.volume === 0) {
    statusMessage.textContent = "No tickets match this filter.";
    metrics.textContent = "Ticket volume: 0 | Median: N/A | SLA: N/A (0 eligible)";
    return;
  }

  statusMessage.textContent = "";

  const overall = summary.overall;
  const median = overall.median_minutes === null
    ? "N/A"
    : `${overall.median_minutes} min`;

  const lines = [
    `Ticket volume: ${overall.volume}`,
    `Median resolution time: ${median} (${overall.resolution_count} valid durations)`,
    `SLA breach rate: ${formatRate(overall.sla_rate)} (${overall.sla_breaches} of ${overall.sla_eligible} eligible)`,
  ];

  for (const line of lines) {
    const paragraph = document.createElement("p");
    paragraph.textContent = line;
    metrics.append(paragraph);
  }

  for (const week of summary.weeks) {
    const row = document.createElement("div");
    row.className = "trend-row";

    const label = document.createElement("div");
    label.textContent = `Week of ${week.week_start}: ${formatRate(week.sla_rate)} (${week.sla_breaches} of ${week.sla_eligible} eligible)`;
    row.append(label);

    if (week.sla_rate !== null) {
      const track = document.createElement("div");
      track.className = "trend-track";
      track.setAttribute("aria-hidden", "true");

      const bar = document.createElement("div");
      bar.className = "trend-bar";
      bar.style.width = `${week.sla_rate * 100}%`;

      track.append(bar);
      row.append(track);
    }

    trend.append(row);
  }
}

async function loadDashboard() {
  try {
    const response = await fetch("./data.json");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    for (const channel of Object.keys(data.channels)) {
      channelSelect.add(new Option(channel, channel));
    }

    channelSelect.addEventListener("change", () => {
      const selectedChannel = channelSelect.value;
      const summary = selectedChannel ? data.channels[selectedChannel] : data;
      renderDashboard(summary);
    });

    renderDashboard(data);
  } catch (error) {
    statusMessage.textContent = "Could not load dashboard data.";
    console.error(error);
  }
}

loadDashboard();