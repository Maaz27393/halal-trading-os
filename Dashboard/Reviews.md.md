---
id: DASH-Review-001
type: dashboard
status: Active
version: 1
created: 2026-08-08
updated: 2026-08-08
owner: Mohammed
---
TABLE
    date AS Date,
    symbol AS Symbol,
    result AS Result,
    review_status AS Status,
    trade AS Trade
FROM "Trade Journal/Post-Trade Reviews"
WHERE type = "review"
SORT date DESC

