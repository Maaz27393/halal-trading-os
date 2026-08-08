# AI Decisions

This note records AI-assisted decisions, recommendations, and approvals related to the Trading OS.

## Purpose

Maintain a transparent record of important AI-assisted decisions without replacing the formal Decision Log.

## Decision Records

```dataview
TABLE
    date AS Date,
    decision AS Decision,
    status AS Status,
    source AS Source
FROM "Automation/AI Workspace"
WHERE type = "ai_decision"
SORT date DESC
```

## Rules

- AI recommendations are not Trading OS rules by themselves.
- Formal Trading OS changes must be recorded in [[Decision Log]].
- AI must distinguish facts, evidence, hypotheses, recommendations, and decisions.
- Preserve the reasoning and source behind important AI-assisted decisions.
- Never overwrite previous decisions.