#!/usr/bin/env python3
"""Lightweight, dependency-free voice-note/transcript analyzer.

Usage:
    python3 scripts/analyze_voice_note.py --transcript path/to/transcript.txt
    python3 scripts/analyze_voice_note.py --text "The learner's transcript here."
    python3 scripts/analyze_voice_note.py --demo

The script accepts transcript text and outputs structure heuristics, filler
word counts, likely strengths/weaknesses, and one suggested next practice
activity. It does not process audio files or infer emotion.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

FILLER_WORDS = {
    "um",
    "uh",
    "like",
    "you know",
    "so",
    "actually",
    "basically",
    "literally",
    "i mean",
    "kind of",
    "sort of",
}

STRUCTURE_MARKERS = {
    "opening": [
        "first",
        "to start",
        "let me explain",
        "the question is",
        "i want to talk about",
        "today i",
    ],
    "closing": [
        "in summary",
        "to conclude",
        "the key takeaway",
        "finally",
        "in conclusion",
        "to sum up",
    ],
    "transition": [
        "next",
        "then",
        "on the other hand",
        "for example",
        "however",
        "therefore",
        "additionally",
        "second",
        "third",
    ],
}

DEMO_TRANSCRIPT = """Um, so I think the main difference is that keyword search looks for exact words and vector search looks for meaning. You know, I would combine them when a query might not have the exact terms but still describes what the user wants."""


def normalize(text: str) -> str:
    # Lowercase, collapse whitespace, keep sentence boundaries.
    text = text.lower()
    text = re.sub(r"[^\w\s\.\,\;\!\?]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def count_filler_words(text: str) -> dict[str, int]:
    normalized = normalize(text)
    counts: dict[str, int] = {}
    for phrase in sorted(FILLER_WORDS, key=len, reverse=True):
        # Count multi-word phrases and single words.
        pattern = re.compile(r"\b" + re.escape(phrase) + r"\b")
        counts[phrase] = len(pattern.findall(normalized))
    return {k: v for k, v in counts.items() if v > 0}


def find_structure_markers(text: str) -> dict[str, list[str]]:
    normalized = normalize(text)
    found: dict[str, list[str]] = {}
    for category, markers in STRUCTURE_MARKERS.items():
        found[category] = [m for m in markers if m in normalized]
    return found


def estimate_word_count(text: str) -> int:
    return len(text.split())


def analyze(text: str) -> dict[str, Any]:
    word_count = estimate_word_count(text)
    filler_counts = count_filler_words(text)
    structure = find_structure_markers(text)
    total_fillers = sum(filler_counts.values())
    filler_ratio = total_fillers / word_count if word_count else 0.0

    strengths: list[str] = []
    improvements: list[str] = []

    if word_count >= 30:
        strengths.append("Answer has enough content to review.")
    else:
        improvements.append("Answer is very short; expand with one concrete example.")

    if structure["opening"]:
        strengths.append("Opening marker detected.")
    else:
        improvements.append("Add a clear opening so the listener knows where the answer is going.")

    if structure["closing"]:
        strengths.append("Closing marker detected.")
    else:
        improvements.append("Add a brief closing summary to reinforce the main point.")

    if structure["transition"]:
        strengths.append("Transition markers detected.")
    else:
        improvements.append("Use explicit transitions between ideas.")

    if total_fillers == 0:
        strengths.append("No common filler words detected.")
    elif filler_ratio < 0.05:
        strengths.append("Filler-word rate is low.")
    else:
        top = sorted(filler_counts.items(), key=lambda x: -x[1])[:2]
        improvements.append(
            f"Filler words detected ({', '.join(f'{k} ({v})' for k, v in top)}). Try pausing instead."
        )

    # Pick one suggested improvement deterministically.
    suggested_next = "Practice the same answer again, focusing on adding a concrete example."
    if improvements:
        if "Add a clear opening" in improvements[0]:
            suggested_next = "Practice one clear opening sentence that states the main point first."
        elif "Add a brief closing" in improvements[0]:
            suggested_next = "Practice ending with one sentence that restates the key takeaway."
        elif "transitions" in improvements[0]:
            suggested_next = "Practice using one explicit transition between your two main points."
        elif "filler words" in improvements[0]:
            suggested_next = "Practice the same answer slowly, replacing filler words with short pauses."
        else:
            suggested_next = improvements[0]

    return {
        "word_count": word_count,
        "filler_word_counts": filler_counts,
        "total_filler_words": total_fillers,
        "structure_markers": structure,
        "likely_strengths": strengths,
        "likely_improvement_areas": improvements,
        "suggested_next_practice": suggested_next,
    }


def print_analysis(result: dict[str, Any]) -> None:
    print(f"Word count: {result['word_count']}")
    print(f"Filler word counts: {result['filler_word_counts']}")
    print("Structure markers found:")
    for category, markers in result["structure_markers"].items():
        print(f"  {category}: {markers if markers else '(none)'}")
    print("Likely strengths:")
    for s in result["likely_strengths"]:
        print(f"  - {s}")
    print("Likely improvement areas:")
    for i in result["likely_improvement_areas"]:
        print(f"  - {i}")
    print("Suggested next practice activity:")
    print(f"  {result['suggested_next_practice']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze a voice-note transcript")
    parser.add_argument("--transcript", help="Path to a transcript text file")
    parser.add_argument("--text", help="Transcript text")
    parser.add_argument("--demo", action="store_true", help="Run on a demo transcript")
    args = parser.parse_args()

    if args.demo:
        text = DEMO_TRANSCRIPT
    elif args.transcript:
        text = Path(args.transcript).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        print("Usage: provide --transcript, --text, or --demo")
        return 1

    result = analyze(text)
    print_analysis(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
