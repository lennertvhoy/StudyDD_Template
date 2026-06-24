#!/usr/bin/env python3
"""Lightweight, dependency-free presentation rehearsal analyzer.

Usage:
    python3 scripts/analyze_presentation_rehearsal.py --transcript path/to/transcript.txt --target-minutes 5
    python3 scripts/analyze_presentation_rehearsal.py --demo

Outputs word count, estimated speaking time, opening/closing detection,
structure markers, jargon warnings, unsupported-claim warnings, and one
suggested improvement. Estimates are heuristic and should not be overclaimed.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

WORDS_PER_MINUTE = 130

OPENING_MARKERS = [
    "today i",
    "in this talk",
    "i want to show",
    "let me start",
    "the goal of",
    "we are here to",
    "my topic is",
]

CLOSING_MARKERS = [
    "in summary",
    "to conclude",
    "in conclusion",
    "the key takeaway",
    "to wrap up",
    "finally",
    "thank you",
]

TRANSITION_MARKERS = [
    "next",
    "then",
    "moving on",
    "on the other hand",
    "for example",
    "however",
    "therefore",
    "additionally",
    "second",
    "third",
]

JARGON_CANDIDATES = [
    "leverage",
    "synergy",
    "disruptive",
    "scalable",
    "holistic",
    "paradigm",
    "actionable",
    "best-in-class",
    "cutting-edge",
    "seamless",
]

CLAIM_PHRASES = [
    "always",
    "never",
    "everyone",
    "nobody",
    "the best",
    "the only",
    "guaranteed",
    "proven",
]

DEMO_TRANSCRIPT = """Today I want to explain why spaced repetition beats cramming. First, cramming feels productive but decays quickly. Next, spaced practice retrieves knowledge at the point of forgetting, which strengthens memory. For example, a single review one day later beats five reviews in one hour. In summary, spaced repetition is the highest-retention move for long-term learning."""


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s\.\,\;\!\?]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def word_count(text: str) -> int:
    return len(text.split())


def estimate_minutes(text: str, wpm: int = WORDS_PER_MINUTE) -> float:
    return round(word_count(text) / wpm, 1)


def has_marker(text: str, markers: list[str]) -> bool:
    normalized = normalize(text)
    return any(marker in normalized for marker in markers)


def find_markers(text: str, markers: list[str]) -> list[str]:
    normalized = normalize(text)
    return [m for m in markers if m in normalized]


def jargon_warnings(text: str) -> list[str]:
    normalized = normalize(text)
    found = [j for j in JARGON_CANDIDATES if j in normalized]
    return found


def unsupported_claim_warnings(text: str) -> list[str]:
    normalized = normalize(text)
    found = [p for p in CLAIM_PHRASES if p in normalized]
    return found


def analyze(text: str, target_minutes: int | None = None) -> dict[str, Any]:
    wc = word_count(text)
    minutes = estimate_minutes(text)
    opening = has_marker(text, OPENING_MARKERS)
    closing = has_marker(text, CLOSING_MARKERS)
    transitions = find_markers(text, TRANSITION_MARKERS)
    jargon = jargon_warnings(text)
    claims = unsupported_claim_warnings(text)

    improvements: list[str] = []
    if not opening:
        improvements.append("Add a clear opening that states the talk's purpose.")
    if not closing:
        improvements.append("Add a closing that reinforces the key takeaway.")
    if not transitions:
        improvements.append("Use explicit transitions so the audience can follow the structure.")
    if jargon:
        improvements.append(f"Jargon-heavy words detected: {', '.join(jargon)}. Consider plain-language alternatives.")
    if claims:
        improvements.append(f"Strong claim words detected: {', '.join(claims)}. Add evidence or soften the claim.")
    if target_minutes and minutes > target_minutes:
        improvements.append(
            f"Estimated time ({minutes} min) exceeds target ({target_minutes} min). Shorten or split content."
        )
    elif target_minutes and minutes < target_minutes * 0.5:
        improvements.append(
            f"Estimated time ({minutes} min) is much shorter than target ({target_minutes} min). Add an example or detail."
        )

    if not improvements:
        suggested = "Rehearse once more and record one thing you can simplify."
    else:
        suggested = improvements[0]

    return {
        "word_count": wc,
        "estimated_speaking_time_minutes": minutes,
        "opening_detected": opening,
        "closing_detected": closing,
        "structure_markers": transitions,
        "jargon_warnings": jargon,
        "unsupported_claim_warnings": claims,
        "suggested_improvement": suggested,
        "target_minutes": target_minutes,
    }


def print_analysis(result: dict[str, Any]) -> None:
    print(f"Word count: {result['word_count']}")
    print(f"Estimated speaking time: {result['estimated_speaking_time_minutes']} minutes")
    print(f"Opening detected: {'yes' if result['opening_detected'] else 'no'}")
    print(f"Closing detected: {'yes' if result['closing_detected'] else 'no'}")
    print(f"Structure markers found: {result['structure_markers'] if result['structure_markers'] else '(none)'}")
    print(f"Jargon warnings (heuristic): {result['jargon_warnings'] if result['jargon_warnings'] else '(none)'}")
    print(f"Unsupported claim warnings (heuristic): {result['unsupported_claim_warnings'] if result['unsupported_claim_warnings'] else '(none)'}")
    print(f"Suggested improvement: {result['suggested_improvement']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze a presentation rehearsal transcript")
    parser.add_argument("--transcript", help="Path to a transcript text file")
    parser.add_argument("--text", help="Transcript text")
    parser.add_argument("--target-minutes", type=int, help="Target presentation length in minutes")
    parser.add_argument("--demo", action="store_true", help="Run on a demo transcript")
    args = parser.parse_args()

    if args.demo:
        text = DEMO_TRANSCRIPT
        target = 3
    elif args.transcript:
        text = Path(args.transcript).read_text(encoding="utf-8")
        target = args.target_minutes
    elif args.text:
        text = args.text
        target = args.target_minutes
    else:
        print("Usage: provide --transcript, --text, or --demo")
        return 1

    result = analyze(text, target_minutes=target)
    print_analysis(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
