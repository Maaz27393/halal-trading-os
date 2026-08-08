---
id: DASH-HOME-001
type: dashboard
status: Active
version: 1.0
created: 2026-08-08
updated: 2026-08-08
owner: Mohammed
---
# 🏠 Halal Trading OS

---

# 📅 Today's Trading

```dataview
TABLE file.mtime AS "Last Updated"
FROM "Trade Journal"
SORT file.mtime DESC
LIMIT 1
```

---

# 📈 Recent Trades

```dataview
TABLE
    date AS Date,
    symbol AS Symbol,
    strategy AS Strategy,
    status AS Status,
    R
FROM "Trade Journal"
WHERE type = "trade"
SORT date DESC
LIMIT 10
```

---

# 📜 Latest Decisions

```dataview
TABLE
    decision_date AS Date,
    decision AS Decision,
    status AS Status
FROM "Decision Log"
WHERE type = "decision"
SORT decision_date DESC
LIMIT 5
```

---

# 📚 Active Strategies

```dataview
TABLE
    status AS Status,
    version AS Version,
    style AS Style,
    timeframe AS Timeframe
FROM "Trading System"
WHERE type = "strategy"
SORT file.name ASC
```

---

# 🔬 Recent Research

```dataview
TABLE
file.mtime AS Updated
FROM "Research"
SORT file.mtime DESC
LIMIT 5
```

---

# 📖 SOP Library

```dataview
LIST
FROM "SOPs"
SORT file.name
```

---

# ⚙️ Trading Rules

```dataview
LIST
FROM "Trading System"
SORT file.name
```


## Claude Operating Context

### Primary Authority

1. [[Trading OS]]
2. [[Decision Log]]
3. [[Entry Rules]]
4. [[Exit Rules]]
5. [[Risk Management]]

### Knowledge Base

- [[Indicators]]
- [[Patterns]]
- [[Candlesticks]]
- [[Market Structure]]

### Intelligence Layer

- [[Trade Journal]]
- [[Reviews]]
- [[Strategies]]
- [[Market]]
- [[Research]]
- [[Decisions]]

### Operating Rules

- Never invent Trading OS rules.
- Treat Decisions Log as the final authority when conflicts exist.
- Separate facts, assumptions, experiments, findings and decisions.
- Research does not become a rule without an explicit decision.
- Historical/reference evidence must not be presented as validated evidence.
- Preserve version history when changing system documentation.

## Quick Navigation

### Trading OS
- [[03_Trading_System]]
- [[Entry Rules]]
- [[Exit Rules]]
- [[Risk Management]]
- [[Decisions Log]]


### Trade Intelligence
- [[Trade Journal]]
- [[Reviews]]
- [[Strategies]]
- [[Market]]
- [[Decisions]]

### Research
- [[Research Dashboard]]
- [[Research Queue]]

### Knowledge Base
- [[Indicators]]
- [[Patterns]]
- [[Candlesticks]]
- [[Market Structure]]

### Current Development
- [[Vault Roadmap]]
- [[Halal Trading OS v1.1 Baseline]]