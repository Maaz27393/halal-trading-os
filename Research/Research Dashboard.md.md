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