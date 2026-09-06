---
type: trade_intelligence_dashboard
version: 1.0
---

# Trade Intelligence

## Recent Trades

```dataview
TABLE
date AS "Date",
symbol AS "Symbol",
strategy AS "Strategy",
status AS "Status",
R AS "R"
FROM "Trade Journal"
WHERE type = "trade"
SORT date DESC
LIMIT 20
```

---

## Trades Requiring Review

```dataview
TABLE
date AS "Date",
symbol AS "Symbol",
strategy AS "Strategy",
status AS "Status"
FROM "Trade Journal"
WHERE type = "trade"
AND review = null
SORT date DESC
```

---

## Recent Post-Trade Reviews

```dataview
TABLE
date AS "Date",
symbol AS "Symbol",
strategy AS "Strategy"
FROM "Trade Journal/Post-Trade Reviews"
WHERE type = "review"
SORT date DESC
LIMIT 20
```

---

## Strategy Distribution

```dataview
TABLE
strategy AS "Strategy",
length(rows) AS "Trades"
FROM "Trade Journal"
WHERE type = "trade"
GROUP BY strategy
SORT length(rows) DESC
```

---

## Market / Sector Distribution

```dataview
TABLE
sector AS "Sector",
length(rows) AS "Trades"
FROM "Trade Journal"
WHERE type = "trade"
GROUP BY sector
SORT length(rows) DESC
```

---

## Recent Trade Decisions

```dataview
TABLE
date AS "Date",
symbol AS "Symbol",
strategy AS "Strategy",
decision AS "Decision"
FROM "Trade Journal"
WHERE type = "trade"
AND decision != null
SORT date DESC
LIMIT 20
```