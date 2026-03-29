import json
from datetime import datetime
import matplotlib.pyplot as plt

FILE = "health_data.json"


def normalize_metric(metric):
    return metric.strip().lower()


def get_status(metric, value):
    metric = metric.lower()

    if metric == "bp":
        if value < 90:
            return "🔻 Low"
        elif value > 140:
            return "🔺 High"
        else:
            return "✅ Normal"

    if metric == "sugar":
        if value < 70:
            return "🔻 Low"
        elif value > 140:
            return "🔺 High"
        else:
            return "✅ Normal"

    return "—"


def load_data():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_health_data(metric, value):
    data = load_data()

    metric = normalize_metric(metric)

    entry = {
        "metric": metric,
        "value": float(value),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    data.append(entry)

    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)


def save_and_message(m, v):
    try:
        save_health_data(m, v)
        return "✅ Saved successfully"
    except:
        return "❌ Error saving data"


def get_history():
    data = load_data()

    if not data:
        return "No data yet."

    data = sorted(data, key=lambda x: x["time"])

    table = "| Metric | Value | Status | Time |\n"
    table += "|--------|-------|--------|------|\n"

    for d in data[-10:]:
        status = get_status(d["metric"], float(d["value"]))
        table += f"| {d['metric']} | {d['value']} | {status} | {d['time']} |\n"

    return table


def get_insights():
    data = load_data()

    if not data:
        return "No data available."

    metrics = {}

    for d in data:
        m = d["metric"]
        v = float(d["value"])
        metrics.setdefault(m, []).append(v)

    output = []

    for m, vals in metrics.items():
        avg = round(sum(vals) / len(vals), 2)
        latest = vals[-1]

        if len(vals) > 1:
            if vals[-1] > vals[0]:
                trend = "increasing 📈"
            elif vals[-1] < vals[0]:
                trend = "decreasing 📉"
            else:
                trend = "stable ➖"
        else:
            trend = "not enough data"

        status = get_status(m, latest)

        output.append(
            f"### {m.upper()}\n"
            f"- Latest: **{latest}** ({status})\n"
            f"- Average: **{avg}**\n"
            f"- Trend: **{trend}**\n"
        )

    return "\n\n".join(output)


def plot_metric(selected_metric):
    data = load_data()

    if not data:
        return None

    vals = [
        float(d["value"])
        for d in data
        if d["metric"] == selected_metric
    ]

    if not vals:
        return None

    fig = plt.figure()
    plt.plot(vals)
    plt.title(f"{selected_metric.upper()} Trend")
    plt.xlabel("Entries")
    plt.ylabel("Value")

    return fig