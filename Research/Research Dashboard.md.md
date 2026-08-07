---
type: research
status:
priority:
---
---
type: research_dashboard
version: 1.0
---

# Research Lab

## Research Pipeline

```dataview
TABLE
status AS "Status",
strategy AS "Strategy",
created AS "Created",
file.link AS "Research"
FROM "Research"
WHERE type = "research"
SORT created DESC
```

---

## 01 — Ideas

```dataview
TABLE
status AS "Status",
strategy AS "Strategy",
created AS "Created",
file.link AS "Research"
FROM "Research/01 Ideas"
SORT file.mtime DESC
```

---

## 02 — Hypotheses

```dataview
TABLE
status AS "Status",
strategy AS "Strategy",
created AS "Created",
file.link AS "Research"
FROM "Research/02 Hypotheses"
SORT file.mtime DESC
```

---

## 03 — Experiments

```dataview
TABLE
status AS "Status",
strategy AS "Strategy",
created AS "Created",
file.link AS "Research"
FROM "Research/03 Experiments"
SORT file.mtime DESC
```

---

## 04 — Backtests

```dataview
TABLE
status AS "Status",
strategy AS "Strategy",
created AS "Created",
file.link AS "Research"
FROM "Research/04 Backtests"
SORT file.mtime DESC
```

---

## 05 — Paper Trading

```dataview
TABLE
status AS "Status",
strategy AS "Strategy",
created AS "Created",
file.link AS "Research"
FROM "Research/05 Paper Trading"
SORT file.mtime DESC
```

---

## 06 — Validation

```dataview
TABLE
status AS "Status",
strategy AS "Strategy",
created AS "Created",
file.link AS "Research"
FROM "Research/06 Validation"
SORT file.mtime DESC
```

---

## 07 — Accepted

```dataview
TABLE
status AS "Status",
strategy AS "Strategy",
created AS "Created",
file.link AS "Research"
FROM "Research/07 Accepted"
SORT file.mtime DESC
```

---

## 08 — Rejected

```dataview
TABLE
status AS "Status",
strategy AS "Strategy",
created AS "Created",
file.link AS "Research"
FROM "Research/08 Rejected"
SORT file.mtime DESC
```

---

## 99 — Archive

```dataview
TABLE
status AS "Status",
strategy AS "Strategy",
created AS "Created",
file.link AS "Research"
FROM "Research/99 Archive"
SORT file.mtime DESC
```


## Research Items Linked to Trading OS

```dataview
TABLE
    file.link AS Research,
    status AS Status,
    priority AS Priority,
    related_strategy AS Strategy
FROM "Research"
WHERE type = "research"
SORT priority DESC
```

## Research Pipeline

```dataview
TABLE WITHOUT ID
    "Hypotheses" AS Stage,
    length(filter(rows, (r) => r.status = "Open")) AS Count
FROM "Research/Hypotheses"
WHERE type = "research"
```

```dataview
TABLE WITHOUT ID
    "Experiments" AS Stage,
    length(rows) AS Count
FROM "Research/Experiments"
WHERE type = "research"
```

```dataview
TABLE WITHOUT ID
    "Validation" AS Stage,
    length(rows) AS Count
FROM "Research/Validation"
WHERE type = "research"
```

```dataview
TABLE WITHOUT ID
    "Accepted" AS Stage,
    length(rows) AS Count
FROM "Research/Accepted"
WHERE type = "research"
```


## Decision Pipeline

```dataview
TABLE
    date AS Date,
    title AS Research,
    evidence_status AS Evidence,
    decision_required AS "Decision Required",
    decision AS Decision,
    file.link AS Research
FROM "Research"
WHERE type = "research"
AND decision_required = true
SORT date DESC
```


## Research Status Overview

```dataview
TABLE WITHOUT ID
    status AS Status,
    length(rows) AS Count
FROM "Research"
WHERE type = "research"
GROUP BY status
SORT Count DESC
```

## Priority Queue

```dataview
TABLE
    date AS Date,
    title AS Research,
    priority AS Priority,
    status AS Status,
    evidence_status AS Evidence,
    file.link AS Research
FROM "Research"
WHERE type = "research"
AND status != "Closed"
SORT priority ASC, date DESC
LIMIT 20
```



