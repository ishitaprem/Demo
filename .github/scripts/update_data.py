from github import Github
import os
import json
from datetime import datetime, timedelta

token = os.getenv("GH_TOKEN")
repo_name = os.getenv("GITHUB_REPOSITORY")
g = Github(token)
repo = g.get_repo(repo_name)

# Status Count
status_counts = {"To Do": 0, "In Progress": 0, "Done": 0}
issues = repo.get_issues(state='all')
for issue in issues:
    if issue.pull_request:
        continue
    for label in issue.labels:
        name = label.name.lower()
        if "to do" in name:
            status_counts["To Do"] += 1
        elif "in progress" in name:
            status_counts["In Progress"] += 1
        elif "done" in name or issue.state == 'closed':
            status_counts["Done"] += 1

# Burndown
today = datetime.utcnow().date()
past_10_days = [today - timedelta(days=i) for i in reversed(range(10))]
burndown_dates = [d.isoformat() for d in past_10_days]
ideal = list(reversed(range(0, len(past_10_days) * 2, 2)))
actual = []
for day in past_10_days:
    count = 0
    for issue in issues:
        if issue.pull_request:
            continue
        if issue.closed_at and issue.closed_at.date() == day:
            count += 1
    actual.append(count)
actual_cumulative = [sum(actual[:i+1]) for i in range(len(actual))]
total = actual_cumulative[-1] + 5
ideal = [total - (i * (total // (len(ideal)-1))) for i in range(len(ideal))]

# Velocity
sprint_labels = {}
for issue in issues:
    if issue.pull_request:
        continue
    sprint = None
    points = 0
    for label in issue.labels:
        if label.name.lower().startswith("sprint"):
            sprint = label.name
        if label.name.isdigit():
            points = int(label.name)
    if sprint:
        sprint_labels.setdefault(sprint, 0)
        if issue.state == 'closed':
            sprint_labels[sprint] += points

# Daily Closed
daily_counts = []
for day in past_10_days:
    count = 0
    for issue in issues:
        if issue.pull_request:
            continue
        if issue.closed_at and issue.closed_at.date() == day:
            count += 1
    daily_counts.append(count)

data = {
    "status": status_counts,
    "burndown": {
        "dates": burndown_dates,
        "ideal": ideal,
        "actual": actual_cumulative
    },
    "velocity": {
        "sprints": list(sprint_labels.keys()),
        "points": list(sprint_labels.values())
    },
    "daily": {
        "dates": burndown_dates,
        "counts": daily_counts
    }
}

with open("dashboard/data.json", "w") as f:
    json.dump(data, f, indent=2)
