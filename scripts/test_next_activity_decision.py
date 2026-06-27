#!/usr/bin/env python3
"""Focused tests for shared StudyDD next-activity decision rules."""

from __future__ import annotations

import sys

from next_activity_decision import choose_activity_decision


TEMPLATES = [
    {
        "activity_type": "recent_info_check",
        "best_for": ["volatile_topic", "it_certification", "live_topic"],
        "expected_evidence": ["source_metadata", "short_summary", "answer_to_check_question"],
    },
    {
        "activity_type": "practical_lab",
        "best_for": ["sysadmin", "cloud", "networking"],
        "expected_evidence": ["screenshot", "command_output", "explanation"],
    },
    {
        "activity_type": "diagram_or_whiteboard",
        "best_for": ["philosophy", "conceptual_understanding"],
        "expected_evidence": ["whiteboard_diagram", "photo"],
    },
]


def decide(**overrides):
    base = {
        "skill_id": None,
        "due_reviews": 0,
        "weakest_skill": None,
        "low_energy": False,
        "target": {"id": "target", "type": "skill", "title": "Target", "volatility": "stable"},
        "study_skill": "generic",
        "recent_types": [],
        "templates": TEMPLATES,
    }
    base.update(overrides)
    return choose_activity_decision(**base)


def test_due_review_beats_everything() -> None:
    decision = decide(
        due_reviews=2,
        low_energy=True,
        target={"type": "certification", "title": "Volatile Cert", "volatility": "volatile"},
        study_skill="practical_lab",
        weakest_skill={"id": "weak", "label": "Weak Skill", "status": "weak", "readiness": 10},
    )
    assert decision.activity_type == "spaced_review"
    assert decision.rule_id == "review_first_due"
    assert "Rule: review-first doctrine" in decision.reason


def test_volatile_target_routes_to_recent_info_check() -> None:
    decision = decide(
        target={"type": "certification", "title": "Volatile Cert", "volatility": "volatile"},
        study_skill="it_certification",
    )
    assert decision.activity_type == "recent_info_check"
    assert decision.rule_id == "volatile_target_needs_recent_info_check"
    assert "Rule: volatile target" in decision.reason


def test_recent_info_check_prevents_immediate_repeat() -> None:
    decision = decide(
        target={"type": "certification", "title": "Volatile Cert", "volatility": "volatile"},
        study_skill="it_certification",
        recent_types=["recent_info_check"],
    )
    assert decision.activity_type == "retrieval_question"
    assert decision.rule_id == "certification_exam_retrieval"
    assert "Rule: certification target" in decision.reason


def test_practical_skill_routes_to_practical_lab() -> None:
    decision = decide(study_skill="cloud")
    assert decision.activity_type == "practical_lab"
    assert decision.rule_id == "hands_on_skill_practical_lab"
    assert "hands-on" in decision.reason


def test_conceptual_skill_routes_to_diagram() -> None:
    decision = decide(study_skill="philosophy")
    assert decision.activity_type == "diagram_or_whiteboard"
    assert decision.rule_id == "conceptual_skill_diagram"
    assert "visual explanation" in decision.reason


def test_certification_practiced_routes_to_retrieval_question() -> None:
    decision = decide(
        target={"type": "certification", "title": "Exam Target", "volatility": "stable"},
        study_skill="it_certification",
        weakest_skill={"id": "exam", "label": "Exam Skill", "status": "pending", "readiness": 45},
    )
    assert decision.activity_type == "retrieval_question"
    assert decision.rule_id == "certification_exam_retrieval"


def test_weak_skill_fallback_routes_to_paper_exercise() -> None:
    decision = decide(
        weakest_skill={"id": "weak", "label": "Weak Skill", "status": "weak", "readiness": 20}
    )
    assert decision.activity_type == "paper_exercise"
    assert decision.rule_id == "weak_skill_paper_exercise"
    assert "Rule: skill 'Weak Skill' is weak" in decision.reason


def test_blocked_skill_fallback_routes_to_explain_back() -> None:
    decision = decide(
        weakest_skill={"id": "blocked", "label": "Blocked Skill", "status": "blocked", "readiness": 10}
    )
    assert decision.activity_type == "explain_back"
    assert decision.rule_id == "blocked_skill_explain_back"
    assert "Rule: skill 'Blocked Skill' is blocked" in decision.reason


def test_low_energy_fallback_routes_to_explain_back() -> None:
    decision = decide(low_energy=True)
    assert decision.activity_type == "explain_back"
    assert decision.rule_id == "low_energy_explain_back"
    assert "Rule: low-energy mode" in decision.reason


def main() -> int:
    tests = [
        test_due_review_beats_everything,
        test_volatile_target_routes_to_recent_info_check,
        test_recent_info_check_prevents_immediate_repeat,
        test_practical_skill_routes_to_practical_lab,
        test_conceptual_skill_routes_to_diagram,
        test_certification_practiced_routes_to_retrieval_question,
        test_weak_skill_fallback_routes_to_paper_exercise,
        test_blocked_skill_fallback_routes_to_explain_back,
        test_low_energy_fallback_routes_to_explain_back,
    ]
    for test in tests:
        print(f"Running {test.__name__}")
        test()
    print("Next activity decision tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
