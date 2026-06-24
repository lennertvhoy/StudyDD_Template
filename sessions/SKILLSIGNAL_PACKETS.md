# SKILLSIGNAL_PACKETS — Proposed Skill Updates

> **Agent-maintained.** Use this file for compact session-to-state update packets.

A SkillSignal packet is a proposed update produced after a question, repair, reflection, or drill. It should be easy to audit before the agent writes durable state changes.

## Packet format

- **Packet ID:**
- **Date:**
- **Target ID:**
- **Skill ID:**
- **Trigger:** question / repair / reflection / override / source update
- **Evidence reference:**
- **Observed signal:** correct / partial / incorrect / unclear / override
- **Proposed status:** confirmed / practiced / weak / pending / blocked
- **Proposed readiness change:**
- **Review action:** add / keep / remove / none
- **Reason:**

## Packets

None yet.
