# Create-Instance Test Pass — StudyDD Demo Path v1

**Date:** 2026-06-24

```bash
python3 scripts/test_create_instance.py
```

Result: **passed**.

The test invoked `scripts/create_instance.py`, which copied the template into a temporary directory, reinitialized Git, switched to `bootstrap` mode, recorded template origin metadata, and passed bootstrap validation.

Key output:

```text
create-instance test passed.
```
