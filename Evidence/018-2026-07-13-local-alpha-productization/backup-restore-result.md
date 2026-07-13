# Backup/restore compatibility

StatePort's deterministic local backup proof restores the synthetic instance to
a new path, validates its identity policy and file hashes, and preserves the
instance lock/source identity. No real backup or learner data is stored in this
evidence directory.
