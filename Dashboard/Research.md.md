TABLE
    date AS Date,
    symbol AS Symbol,
    trade AS Trade,
    strategy AS Strategy
FROM "Trade Journal/Post-Trade Reviews"
WHERE type = "review"
AND contains(file.text, "Research required")
SORT date DESC