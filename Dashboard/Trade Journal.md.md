# Trade Intelligence Dashboard

## Recent Trades

````
```text
```dataview
TABLE
    date AS Date,
    symbol AS Symbol,
    direction AS Direction,
    strategy AS Strategy,
    setup AS Setup,
    market_condition AS "Market",
    sector AS Sector,
    R,
    review_status AS "Review"
FROM "Trade Journal"
WHERE type = "trade"
SORT date DESC
LIMIT 20
````