# SESSION_LOG — AI-103 Example

## Session 2026-06-23 — Azure AI Search and RAG exam drill

- **Focus:** Azure AI Search and RAG
- **Questions asked:** Q-20260623-001, Q-20260623-002, Q-20260623-003
- **Result summary:**
  - Strong on hybrid search configuration.
  - Correctly mapped indexer pipeline stages.
  - Partial on semantic ranking parameter tuning.
- **Evidence added:**
  - E-20260623-001 — correct hybrid search explanation
  - E-20260623-002 — correct indexer pipeline mapping
  - E-20260623-003 — partial semantic ranking answer
- **Mistake tags:**
  - E-20260623-003: correct-concept-weak-implementation
- **Option randomization example:**
  - Q-20260623-002: final order C, A, D, B; correct label C
- **Reviews added:**
  - R-20260624-AI103-003 — review semantic ranking knobs
- **State changes:**
  - `ai103-search-rag` readiness 70 -> 80
- **Next action proposed:** Drill semantic ranking knobs in the next session, then move to Foundry evaluations.

## Session 2026-06-22 — Foundry evaluations and agents

- **Focus:** Azure AI Foundry evaluations and AI agents
- **Questions asked:** Q-20260622-001, Q-20260622-002
- **Result summary:**
  - Partial on custom evaluation metrics; missed safety evaluator integration.
  - Incorrect on tool-call orchestration pattern.
- **Evidence added:**
  - E-20260622-001 — partial eval metrics answer
  - E-20260622-002 — incorrect agent tool-call answer
- **Mistake tags:**
  - E-20260622-001: correct-concept-weak-implementation
  - E-20260622-002: service-boundary-confusion
- **Reviews added:**
  - R-20260624-AI103-001 — review evaluation flows
  - R-20260624-AI103-002 — review agent tool-call orchestration
- **State changes:**
  - `ai103-foundry-eval` marked weak
  - `ai103-agents` marked weak
- **Next action proposed:** Revisit evaluation docs and a simple agent trace example.
