# CI workflow update

New validation steps added to `.github/workflows/validate.yml`:

      - name: Run source freshness test
        run: python3 scripts/test_source_freshness.py

      - name: Run question quality test
        run: python3 scripts/test_question_quality.py

      - name: Run learner adaptation test
        run: python3 scripts/test_learner_adaptation.py

      - name: Check source freshness for demo target
        run: python3 scripts/check_source_freshness.py --target-id demo-ai-search-exam --now "2026-06-24T12:00:00+00:00"

