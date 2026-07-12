# Changed contracts

- Source checks write only in `learner_instance` mode and use atomic replacement.
- Recorded check outcomes feed the single freshness classifier.
- Fast Drill checkpoints are versioned and hash-linked; recovery and closure
  are transactional and idempotent.
- Question records require stable structured identity and provenance; private
  learner state is outside the template question-bank boundary.
