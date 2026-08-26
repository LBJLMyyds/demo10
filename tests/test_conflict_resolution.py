"""Tests for review-only, recency-weighted conflict resolution."""

from __future__ import annotations

import unittest

import pandas as pd

from src.pipeline.clean import build_conflict_candidates


def reviews(*rows: dict[str, object]) -> pd.DataFrame:
    """Create the minimum review-shaped frame needed by the conflict engine."""
    defaults = {
        "stable_ramp": None,
        "acs_bathroom": None,
        "acs_seating": None,
        "acs_parking": None,
    }
    return pd.DataFrame([{**defaults, **row} for row in rows])


class ReviewRecencyConflictTests(unittest.TestCase):
    def test_recent_review_can_outweigh_old_majority(self) -> None:
        frame = reviews(
            {"review_id": "old-1", "place_id": "p1", "stable_ramp": "no", "reviewed_at": "2020-01-01T00:00:00Z"},
            {"review_id": "old-2", "place_id": "p1", "stable_ramp": "no", "reviewed_at": "2020-02-01T00:00:00Z"},
            {"review_id": "new", "place_id": "p1", "stable_ramp": "yes", "reviewed_at": "2026-01-01T00:00:00Z"},
        )

        result = build_conflict_candidates(frame)

        self.assertEqual(len(result), 1)
        candidate = result.iloc[0]
        self.assertEqual(candidate["proposed_value"], "yes")
        self.assertEqual(candidate["status"], "provisional")
        self.assertEqual(candidate["evidence_quality"], "high")
        self.assertGreater(candidate["yes_weight"], candidate["no_weight"])
        self.assertEqual(candidate["latest_review_ids"], "new")

    def test_undated_opposing_evidence_forces_human_review(self) -> None:
        frame = reviews(
            {"review_id": "dated", "place_id": "p1", "acs_bathroom": "yes", "reviewed_at": "2026-01-01T00:00:00Z"},
            {"review_id": "undated", "place_id": "p1", "acs_bathroom": "no", "reviewed_at": None},
        )

        candidate = build_conflict_candidates(frame).iloc[0]

        self.assertEqual(candidate["proposed_value"], "yes")
        self.assertEqual(candidate["status"], "human_review")
        self.assertEqual(candidate["needs_human_review"], 1)
        self.assertEqual(candidate["resolution_score"], 0.5)
        self.assertEqual(candidate["evidence_quality"], "low")

    def test_default_half_life_prioritises_review_120_days_newer(self) -> None:
        frame = reviews(
            {"review_id": "old", "place_id": "p1", "stable_ramp": "no", "reviewed_at": "2025-01-01T00:00:00Z"},
            {"review_id": "new", "place_id": "p1", "stable_ramp": "yes", "reviewed_at": "2025-05-01T00:00:00Z"},
        )

        candidate = build_conflict_candidates(frame).iloc[0]

        self.assertEqual(candidate["proposed_value"], "yes")
        self.assertEqual(candidate["status"], "provisional")
        self.assertEqual(candidate["evidence_quality"], "medium")
        self.assertGreaterEqual(candidate["resolution_score"], 0.60)

    def test_equal_dated_weights_remain_unresolved(self) -> None:
        frame = reviews(
            {"review_id": "yes", "place_id": "p1", "acs_seating": "yes", "reviewed_at": "2026-01-01T00:00:00Z"},
            {"review_id": "no", "place_id": "p1", "acs_seating": "no", "reviewed_at": "2026-01-01T00:00:00Z"},
        )

        candidate = build_conflict_candidates(frame).iloc[0]

        self.assertEqual(candidate["proposed_value"], "unresolved")
        self.assertEqual(candidate["status"], "human_review")
        self.assertEqual(candidate["resolution_score"], 0.0)
        self.assertEqual(candidate["evidence_quality"], "low")

    def test_non_conflicting_reviews_do_not_create_candidate(self) -> None:
        frame = reviews(
            {"review_id": "one", "place_id": "p1", "acs_parking": "yes", "reviewed_at": "2025-01-01T00:00:00Z"},
            {"review_id": "two", "place_id": "p1", "acs_parking": "yes", "reviewed_at": "2026-01-01T00:00:00Z"},
        )

        result = build_conflict_candidates(frame)

        self.assertTrue(result.empty)
        self.assertIn("resolution_score", result.columns)

    def test_parameters_are_validated(self) -> None:
        frame = reviews(
            {"review_id": "one", "place_id": "p1", "stable_ramp": "yes", "reviewed_at": "2026-01-01T00:00:00Z"}
        )
        with self.assertRaises(ValueError):
            build_conflict_candidates(frame, half_life_days=0)
        with self.assertRaises(ValueError):
            build_conflict_candidates(frame, resolution_threshold=1.1)
        with self.assertRaises(ValueError):
            build_conflict_candidates(frame, resolution_threshold=0.8, high_quality_threshold=0.7)


if __name__ == "__main__":
    unittest.main()
