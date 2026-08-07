TABLE
    date AS Date,
    symbol AS Symbol,
    result AS Result,
    review_status AS Status,
    trade AS Trade
FROM "Trade Journal/Post-Trade Reviews"
WHERE type = "review"
SORT date DESC