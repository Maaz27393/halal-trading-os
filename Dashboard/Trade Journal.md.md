```dataview
TABLE
    date AS Date,
    symbol AS Symbol,
    direction AS Direction,
    strategy AS Strategy,
    setup AS Setup,
    market_condition AS Market,
    sector AS Sector,
    R,
    review_status AS Review
FROM "Trade Journal"
WHERE type = "trade"
SORT date DESC
LIMIT 20
```

## Post-Trade Reviews

```dataview
TABLE
    date AS Date,
    symbol AS Symbol,
    result AS Result,
    strategy AS Strategy,
    market_condition AS Market,
    sector AS Sector,
    review_status AS Status
FROM "Trade Journal"
WHERE type = "review"
SORT date DESC
LIMIT 20
```

## Strategy Performance

```dataview
TABLE WITHOUT ID
    strategy AS Strategy,
    length(rows) AS Trades,
    round(sum(rows.R), 2) AS "Total R",
    round(average(rows.R), 2) AS "Average R"
FROM "Trade Journal"
WHERE type = "trade" AND strategy
GROUP BY strategy
SORT "Total R" DESC
```
## Market Condition Intelligence

```dataview
TABLE WITHOUT ID
    market_condition AS "Market Condition",
    length(rows) AS Trades,
    round(sum(rows.R), 2) AS "Total R",
    round(average(rows.R), 2) AS "Average R"
FROM "Trade Journal"
WHERE type = "trade" AND market_condition
GROUP BY market_condition
SORT "Total R" DESC
```
## Sector Intelligence

```dataview
TABLE WITHOUT ID
    sector AS Sector,
    length(rows) AS Trades,
    round(sum(rows.R), 2) AS "Total R",
    round(average(rows.R), 2) AS "Average R"
FROM "Trade Journal"
WHERE type = "trade" AND sector
GROUP BY sector
SORT "Total R" DESC
```




```dataview
TABLE
    date AS Date,
    symbol AS Symbol,
    strategy AS Strategy,
    result AS Result,
    review_status AS Status,
    file.link AS Review
FROM "Trade Journal/Post-Trade Reviews"
WHERE type = "review"
AND research_required = true
SORT date DESC
```
