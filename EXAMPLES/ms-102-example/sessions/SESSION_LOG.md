# SESSION_LOG — MS-102 Example

## Session 2026-06-23 — Microsoft 365 tenant administration exam drill

- **Focus:** Microsoft 365 tenant administration
- **Questions asked:** Q-20260623-001, Q-20260623-002, Q-20260623-003
- **Result summary:**
  - Strong on tenant configuration.
  - Correctly mapped license and role assignment flow.
  - Partial on security baseline tuning.
- **Evidence added:**
  - E-20260623-001 — correct tenant configuration explanation
  - E-20260623-002 — correct license and role assignment mapping
  - E-20260623-003 — partial security baseline answer
- **Mistake tags:**
  - E-20260623-003: correct-concept-weak-implementation
- **Option randomization example (recorded after grading):**
  - Q-20260623-002:
    - Internal option IDs before shuffle:
      - opt_1 = Use a single global administrator account [distractor]
      - opt_2 = Disable all user self-service settings [distractor]
      - opt_3 = Combine least-privilege roles, conditional access, and audit review [correct]
      - opt_4 = Assign broad admin roles without review [distractor]
    - Final visible order: C = opt_1, A = opt_2, D = opt_4, B = opt_3
    - Correct visible label: B
    - Learner answer: B
    - Grading result: correct
- **Reviews added:**
  - R-20260624-MS102-003 — review security baseline controls
- **State changes:**
  - `ms102-tenant-admin` readiness 70 -> 80
- **Next action proposed:** Drill security baseline controls in the next session, then move to security posture.

## Session 2026-06-22 — security posture and endpoint management

- **Focus:** Microsoft 365 security posture and device management
- **Questions asked:** Q-20260622-001, Q-20260622-002
- **Result summary:**
  - Partial on custom security alerts; missed admin-center signal correlation.
  - Incorrect on device enrollment policy pattern.
- **Evidence added:**
  - E-20260622-001 — partial security alert handling answer
  - E-20260622-002 — incorrect device enrollment answer
- **Mistake tags:**
  - E-20260622-001: correct-concept-weak-implementation
  - E-20260622-002: service-boundary-confusion
- **Reviews added:**
  - R-20260624-MS102-001 — review security posture signals
  - R-20260624-MS102-002 — review device enrollment policy
- **State changes:**
  - `ms102-security-posture` marked weak
  - `ms102-endpoint management` marked weak
- **Next action proposed:** Revisit Microsoft Defender and admin center docs and a simple device compliance example.
