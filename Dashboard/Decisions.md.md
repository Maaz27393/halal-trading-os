---
id: DASH-Decision-001
type: dashboard
status: Active
version: 1
created: 2026-08-08
updated: 2026-08-08
owner: Mohammed
---
## Recent Decisions

```dataview
TABLE
    date AS Date,
    id AS ID,
    status AS Status,
    file.link AS Decision
FROM "Decisions"
WHERE type = "decision"
SORT date DESC
LIMIT 10
```

# Trading OS v2.0 — Change Register

| ID     | Area                  | Change                                               | Evidence         | Status      |
| ------ | --------------------- | ---------------------------------------------------- | ---------------- | ----------- |
| V2-001 | Trade Intelligence    | Structured trade → review connection                 | GABRIEL trade    | Implemented |
| V2-002 | Dashboard             | Trade Intelligence dashboard                         | Dataview         | Implemented |
| V2-003 | Strategy Intelligence | Strategy performance tracking                        | Dataview         | Implemented |
| V2-004 | Market Intelligence   | Market-condition tracking                            | Dataview         | Implemented |
| V2-005 | Sector Intelligence   | Sector tracking                                      | Dataview         | Implemented |
| V2-006 | Review Intelligence   | Rule adherence / psychology / lessons / improvements | GABRIEL review   | Implemented |
| V2-007 | Research Feedback     | Review → Research flag                               | Not yet reliable | Pending     |
| V2-008 | Version Control       | v2.0 development tracking                            | Vault Roadmap    | Implemented |

## Research Awaiting Decision

```dataview
TABLE
    date AS Date,
    title AS Research,
    evidence_status AS Evidence,
    related_strategy AS Strategy,
    file.link AS Research
FROM "Research"
WHERE type = "research"
AND decision_required = true
SORT date DESC
```
