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
strategy,
status,
date
FROM "Trade Journal"
SORT date DESC
LIMIT 10
```

---

# 📜 Latest Decisions

```dataview
TABLE
status,
date
FROM "Decision Log"
SORT file.mtime DESC
LIMIT 5
```

---

# 📚 Active Strategies

```dataview
TABLE
status,
version
FROM "Strategies"
SORT file.name
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