# Local AI System Specification

## 1. Purpose

This workspace defines the local AI integration for the halal-trading-os Obsidian vault.

The AI system must use the Obsidian vault as its primary source of truth.

## 2. Core Model

Primary local reasoning model:

- Qwen3 4B
- Runtime: Ollama

## 3. Privacy Principle

Sensitive vault information must remain local.

The system must not automatically send vault contents, memory, trade history, research, decisions, or other private information to cloud AI services.

External services may be accessed through explicitly configured local tools when required, but returned information must remain local unless the user explicitly chooses otherwise.

## 4. Source of Truth Hierarchy

When information conflicts, use this priority:

1. Trading System
2. Decision Log
3. Approved Strategies
4. Approved SOPs
5. Research findings
6. Trade Journal and Post-Trade Reviews
7. Knowledge Base
8. Other supporting material

The AI must not invent or silently modify trading rules.

## 5. Knowledge vs Experience

The AI must distinguish between:

- Established knowledge
- Approved trading rules
- Decisions
- Strategies
- SOPs
- Research hypotheses
- Research findings
- Trade observations
- Trade reviews
- Personal lessons
- Unverified assumptions

Unverified information must not be presented as an approved rule.

## 6. Obsidian as Source of Truth

The AI should retrieve information from the vault when answering questions about the user's trading system, strategies, procedures, research, decisions, journal, or documented experience.

The AI should prefer the most authoritative relevant document rather than relying on its pretrained knowledge.

## 7. Memory

Durable AI memory must be separate from ordinary knowledge.

Memory should contain only information that is useful across future interactions and should not duplicate the entire Obsidian knowledge base.

## 8. Skills

Reusable workflows should eventually be implemented as local skills.

Skills must not create or change trading rules unless the user explicitly approves the change.

## 9. Tools

Tools must be treated separately from knowledge and skills.

Read-only tools should be preferred initially.

Tools capable of modifying data or executing consequential actions require explicit user approval.

## 10. Change Control

The AI must not automatically modify authoritative trading documents.

Any proposed change to:

- Trading System
- Trading OS
- Decision Log
- Strategies
- SOPs

must be presented to the user for approval before being committed.

## 11. Git Version Control

The vault is maintained under Git version control.

AI-generated changes should be reviewable through Git before they are considered final.

## 12. Development Principle

Build incrementally:

Obsidian
→ Local Retrieval
→ Qwen3
→ Memory
→ Skills
→ Agent Runtime
→ Local Tools
→ External Read-Only Data
→ Controlled Actions

Do not bypass these stages.