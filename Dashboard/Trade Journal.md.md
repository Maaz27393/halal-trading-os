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
## Research Required 

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

## Trade Quality

```dataview
TABLE
    date AS Date,
    symbol AS Symbol,
    strategy AS Strategy,
    review_status AS Status,
    file.link AS Review
FROM "Trade Journal/Post-Trade Reviews"
WHERE type = "review"
SORT date DESC
LIMIT 20
```
## Psychology Intelligence

```dataview
TABLE
    date AS Date,
    symbol AS Symbol,
    confidence AS Confidence,
    fear AS Fear,
    greed AS Greed,
    fomo AS FOMO,
    patience AS Patience,
    discipline AS Discipline,
    file.link AS Review
FROM "Trade Journal/Post-Trade Reviews"
WHERE type = "review"
SORT date DESC
LIMIT 20
```
## Rule Adherence

```dataview
TABLE
    date AS Date,
    symbol AS Symbol,
    strategy AS Strategy,
    entry_rules_followed AS Entry,
    exit_rules_followed AS Exit,
    risk_rules_followed AS Risk,
    sop_followed AS SOP,
    file.link AS Review
FROM "Trade Journal/Post-Trade Reviews"
WHERE type = "review"
SORT date DESC
LIMIT 20
```
## Execution Errors

```dataview
TABLE
    date AS Date,
    symbol AS Symbol,
    strategy AS Strategy,
    execution_errors AS "Errors",
    file.link AS Review
FROM "Trade Journal/Post-Trade Reviews"
WHERE type = "review"
SORT date DESC
LIMIT 20
```
## Lessons

```dataview
TABLE
    date AS Date,
    symbol AS Symbol,
    strategy AS Strategy,
    lessons AS Lessons,
    file.link AS Review
FROM "Trade Journal/Post-Trade Reviews"
WHERE type = "review"
SORT date DESC
LIMIT 20
```
## Improvements

```dataview
TABLE
    date AS Date,
    symbol AS Symbol,
    strategy AS Strategy,
    improvements AS Improvements,
    file.link AS Review
FROM "Trade Journal/Post-Trade Reviews"
WHERE type = "review"
SORT date DESC
LIMIT 20
```
## Trade Intelligence Summary

```dataview
TABLE
    date AS Date,
    symbol AS Symbol,
    strategy AS Strategy,
    R,
    review_status AS Review
FROM "Trade Journal"
WHERE type = "trade"
SORT date DESC
LIMIT 20
```
## Dashboard Status

```dataview
TABLE WITHOUT ID
    length(rows) AS "Total Trades",
    round(sum(rows.R), 2) AS "Total R",
    round(average(rows.R), 2) AS "Average R"
FROM "Trade Journal"
WHERE type = "trade"
```
## Recent Decisions

```dataview
TABLE
    date AS Date,
    decision_type AS Type,
    status AS Status,
    summary AS Summary,
    file.link AS Decision
FROM "Decisions"
SORT date DESC
LIMIT 10
```

## Today's Trades

```dataview
TABLE
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
AND date = date(today)
SORT symbol ASC
```

## R Performance

```dataview
TABLE WITHOUT ID
    "Trades" AS Metric,
    length(rows) AS Value
FROM "Trade Journal"
WHERE type = "trade"
```

```dataview
TABLE WITHOUT ID
    "Total R" AS Metric,
    round(sum(R), 2) AS Value
FROM "Trade Journal"
WHERE type = "trade"
```

```dataview
TABLE WITHOUT ID
    "Average R" AS Metric,
    round(average(R), 2) AS Value
FROM "Trade Journal"
WHERE type = "trade"
```
## Win Rate

```dataview
TABLE WITHOUT ID
    "Winning Trades" AS Metric,
    length(filter(rows, (r) => r.R > 0)) AS Value
FROM "Trade Journal"
WHERE type = "trade"
```

```dataview
TABLE WITHOUT ID
    "Losing Trades" AS Metric,
    length(filter(rows, (r) => r.R < 0)) AS Value
FROM "Trade Journal"
WHERE type = "trade"
```

```dataview
TABLE WITHOUT ID
    "Win Rate" AS Metric,
    round(100 * length(filter(rows, (r) => r.R > 0)) / length(rows), 1) + "%" AS Value
FROM "Trade Journal"
WHERE type = "trade"
```
