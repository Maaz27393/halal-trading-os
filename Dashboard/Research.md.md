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
    file.link AS Experiment,
    status AS Status,
    created AS Created,
    strategy AS Strategy,
    sector AS Sector,
    market_condition AS Market Condition,
    hypothesis AS Hypothesis
FROM "Research/Experiments"
WHERE type = "research"
SORT created DESC
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
