---
id: DASH-Research-001
type: dashboard
status: Active
version: 1
created: 2026-08-08
updated: 2026-08-08
owner: Mohammed
---
# Research Queue

## Open Research

```dataview
TABLE
    id AS ID,
    date AS Date,
    title AS Research,
    priority AS Priority,
    evidence_status AS Evidence,
    related_strategy AS Strategy,
    file.link AS Research
FROM "Research"
WHERE type = "research"
AND status != "Closed"
SORT priority DESC, date DESC
```

## Active Experiments

```dataview
TABLE
    date AS Date,
    title AS Experiment,
    status AS Status,
    research AS Research,
    strategy AS Strategy,
    evidence_status AS Evidence,
    file.link AS Experiment
FROM "Research/Experiments"
WHERE type = "research"
SORT date DESC
```

## Research Requiring Decision

```dataview
TABLE
    id AS ID,
    date AS Date,
    title AS Research,
    evidence_status AS Evidence,
    related_strategy AS Strategy,
    file.link AS Research
FROM "Research"
WHERE type = "research"
AND decision_required = true
SORT date DESC
```
