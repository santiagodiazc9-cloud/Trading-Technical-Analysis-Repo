---
type: adr
date: {{date:YYYY-MM-DD}}
status: Accepted
supersedes: none
tags:
  - adr
  - rule-change
---

# ADR-NNNN: <decision title>

**Date**: {{date:YYYY-MM-DD}}
**Status**: Accepted
**Supersedes**: <ADR-NNNN if any, else "none">

## Context
What was happening this week that motivated the change. Cite specific trades, journal entries (e.g., [[2026-05-08]]), or memory files (e.g., [[learnings]]).

## Decision
The exact rule change. Before → after. Be specific about thresholds and conditions.

## Consequences
- **Positive**: what this prevents or improves
- **Negative**: what we're giving up or risking
- **Neutral**: behavior unchanged in these scenarios

## Validation Plan
How we'll know if this was the right call. Concrete metric + timeframe.
> e.g., "If win rate of trades caught by this rule drops < 40% over next 10 samples, revisit."

## References
- Memory: [[learnings]] / [[strategy]]
- Trades: [[journal/YYYY-MM-DD]] — TICKER
- RuFlo namespace: `trading` / key:
