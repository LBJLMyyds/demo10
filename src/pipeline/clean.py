"""Clean and standardise various accessibility datasets."""

from __future__ import annotations

import hashlib
import re

import pandas as pd


def snake_case(names: list) -> list:
    """Convert list of strings into snake_case."""
    return [re.sub(r'[^a-zA-Z0-9]+', "_", s.lower()).strip("_") for s in names]


def clean_reference_map_points(df: pd.DataFrame, source: str) -> pd.DataFrame:
    """Standardise data points from manually extracted from PDF maps.""" 

    df.columns = snake_case(df.columns)
    df = df.rename(columns={"x": "lng", "y": "lat", "fid": "point_id"})

    for col in ["lng", "lat"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    df["point_id"] = df["point_id"].str.upper()
    df["facility_type"] = df["facility_type"].str.lower()
    df["source_id"] = source

    df = df.dropna(subset=["lng", "lat"], ignore_index=True)
    df = df.drop_duplicates(keep="first", ignore_index=True)

    return df


def clean_places(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise EnAccess place-aggregated data."""

    df.columns = snake_case(df.columns)

    # Can't drop malformed rows as foreign key constraints will fail
    # Assume data will be not malformed and drop irrelevant columns for now
    malformed = [c for c in df.columns if c.startswith("unnamed")]
    df = df.drop(malformed, axis=1)

    # Enforce column data types
    num_cols = ["lat", "lng", "avg_rating"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        
    count_cols = ["review_count"] + [c for c in df.columns if c.startswith(
        ("steps_", "ramp_", "bathroom_", "seating_", "parking_"))]
    for col in count_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    
    str_cols = list(set(df.columns) - set(count_cols) - set(num_cols))
    for col in str_cols:
        df[col] = df[col].fillna("").astype(str).str.strip()

    # Remove duplicate tags and sort alphabetically
    df["category_tags"] = df["category_tags"].str.split("|").map(
        lambda x: "|".join(sorted(set(x))), na_action="ignore")

    df = df.drop_duplicates(subset="place_id", keep="last", ignore_index=True)

    return df


def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise EnAccess review data."""    

    df.columns = snake_case(df.columns)

    malformed = [c for c in df.columns if c.startswith("unnamed")]
    df = df.drop(malformed, axis=1)

    # Enforce column data types
    num_cols = ["lat", "lng", "rating"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["lat", "lng"])

    df["steps_on_entry"] = [int(i) if i != "4+" else 4 
                            for i in df["steps_on_entry"]]

    feature_cols = ["stable_ramp", "acs_bathroom", "acs_seating", "acs_parking"]
    for col in feature_cols:
        df[col] = df[col].fillna("unsure").astype(str).str.lower().str.strip()

    str_cols = list(set(df.columns) - set(num_cols) - set(feature_cols)
                     - set(["steps_on_entry"]))
    for col in str_cols:
        df[col] = df[col].fillna("").astype(str).str.strip()

    df = df.drop_duplicates(subset="review_id", keep="first", ignore_index=True)

    return df


YES_VALUES = {"yes", "true", "t", "1", "y"}
NO_VALUES = {"no", "false", "f", "0", "n"}
UNSURE_VALUES = {"unsure", "unknown", "not sure", "na", "n/a", ""}

REVIEW_FEATURE_COLUMNS = {
    "stable_ramp": "ramp",
    "acs_bathroom": "bathroom",
    "acs_seating": "seating",
    "acs_parking": "parking",
}

CONFLICT_CANDIDATE_COLUMNS = [
    "candidate_id",
    "place_id",
    "feature_type",
    "conflict_type",
    "yes_count",
    "no_count",
    "unsure_count",
    "dated_evidence_count",
    "latest_reviewed_at",
    "latest_review_ids",
    "yes_weight",
    "no_weight",
    "unsure_weight",
    "proposed_value",
    "resolution_method",
    "resolution_score",
    "evidence_quality",
    "status",
    "needs_human_review",
    "notes",
]


def standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with snake_case column names and unnamed columns removed."""
    cleaned = df.copy()
    columns = []
    for column in cleaned.columns:
        name = str(column).strip()
        name = re.sub(r"[^0-9a-zA-Z]+", "_", name)
        name = re.sub(r"_+", "_", name).strip("_").lower()
        columns.append(name)
    cleaned.columns = columns
    unnamed = [column for column in cleaned.columns if column.startswith("unnamed")]
    return cleaned.drop(columns=unnamed, errors="ignore")


def stable_id(*parts: object, length: int = 16) -> str:
    """Create a deterministic short ID from text-like parts."""
    raw = "|".join("" if part is None else str(part) for part in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:length]


def normalise_boolean(value: object) -> object:
    """Convert mixed boolean-like values to 1, 0, or None."""
    if pd.isna(value):
        return None
    if isinstance(value, bool):
        return int(value)
    text = str(value).strip().lower()
    if text in YES_VALUES:
        return 1
    if text in NO_VALUES:
        return 0
    return None


def normalise_yes_no_unsure(value: object) -> object:
    """Convert accessibility review values to yes, no, unsure, or None."""
    if pd.isna(value):
        return None
    if isinstance(value, bool):
        return "yes" if value else "no"
    text = str(value).strip().lower()
    if text in YES_VALUES:
        return "yes"
    if text in NO_VALUES:
        return "no"
    if text in UNSURE_VALUES:
        return "unsure"
    return None


def clean_toilets(raw_accessible_toilets: pd.DataFrame, raw_melbourne_toilets: pd.DataFrame) -> pd.DataFrame:
    """Combine national and City of Melbourne public toilet exports."""
    national = standardise_columns(raw_accessible_toilets)
    melbourne = standardise_columns(raw_melbourne_toilets)

    national_rows = pd.DataFrame(
        {
            "toilet_id": "nat_" + national["facilityid"].astype(str),
            "source_id": "accessible_toilets_15_councils",
            "source_toilet_id": national["facilityid"].astype(str),
            "name": national.get("name"),
            "address": national.get("address1"),
            "town": national.get("town"),
            "state": national.get("state"),
            "lat": pd.to_numeric(national.get("latitude"), errors="coerce"),
            "lng": pd.to_numeric(national.get("longitude"), errors="coerce"),
            "accessible": national.get("accessible").apply(normalise_boolean),
            "parking_accessible": national.get("parkingaccessible").apply(normalise_boolean),
            "opening_hours": national.get("openinghours"),
            "council": national.get("lga_name"),
        }
    )

    melbourne_rows = pd.DataFrame(
        {
            "toilet_id": ["mel_" + stable_id(name, idx) for idx, name in enumerate(melbourne.get("name", []))],
            "source_id": "melbourne_public_toilets",
            "source_toilet_id": melbourne.index.astype(str),
            "name": melbourne.get("name"),
            "address": None,
            "town": "Melbourne",
            "state": "VIC",
            "lat": pd.to_numeric(melbourne.get("lat"), errors="coerce"),
            "lng": pd.to_numeric(melbourne.get("lon"), errors="coerce"),
            "accessible": melbourne.get("wheelchair").apply(normalise_boolean),
            "parking_accessible": None,
            "opening_hours": None,
            "council": "MELBOURNE",
        }
    )

    df = pd.concat([national_rows, melbourne_rows], ignore_index=True)
    return df.drop_duplicates(subset=["toilet_id"], keep="first")


def clean_tactile_indicators(raw_tactile: pd.DataFrame) -> pd.DataFrame:
    """Clean tactile ground surface indicator point assets."""
    df = standardise_columns(raw_tactile)
    result = pd.DataFrame(
        {
            "asset_id": df.get("asset_number").astype(str),
            "description": df.get("asset_description"),
            "road_segment": df.get("road_segment"),
            "lat": pd.to_numeric(df.get("lat"), errors="coerce"),
            "lng": pd.to_numeric(df.get("lon"), errors="coerce"),
            "source_id": "tactile_ground_surface_indicators",
        }
    )
    return result.drop_duplicates(subset=["asset_id"], keep="first")


def clean_council_reference(raw_councils: pd.DataFrame) -> pd.DataFrame:
    """Clean the inherited council accessibility data catalogue."""
    df = standardise_columns(raw_councils)
    result = pd.DataFrame(
        {
            "council_id": [stable_id(name, idx) for idx, name in enumerate(df.get("council", []))],
            "council": df.get("council"),
            "town": df.get("town"),
            "accessibility_categories": df.get("accessibility_categories"),
            "format": df.get("format"),
            "last_updated": df.get("last_updated"),
            "link": df.get("link"),
            "constraints": df.get("missing_data_constraints"),
        }
    )
    return result.drop_duplicates(subset=["council_id"], keep="first")


def build_accessibility_features(places: pd.DataFrame, reviews: pd.DataFrame) -> pd.DataFrame:
    """Create a unified accessibility feature table from aggregate and review data."""
    rows: list[dict[str, object]] = []
    feature_groups = {
        "ramp": ("ramp_yes", "ramp_no", "ramp_unsure"),
        "bathroom": ("bathroom_yes", "bathroom_no", "bathroom_unsure"),
        "seating": ("seating_yes", "seating_no", "seating_unsure"),
        "parking": ("parking_yes", "parking_no", "parking_unsure"),
    }
    for _, row in places.iterrows():
        for feature_type, columns in feature_groups.items():
            counts = {"yes": int(row[columns[0]]), "no": int(row[columns[1]]), "unsure": int(row[columns[2]])}
            total = sum(counts.values())
            if total == 0:
                continue
            value = max(counts, key=counts.get)
            rows.append(
                {
                    "feature_id": stable_id("places", row["place_id"], feature_type),
                    "place_id": row["place_id"],
                    "review_id": None,
                    "feature_type": feature_type,
                    "value": value,
                    "source_id": "enaccess_places",
                    "confidence": round(counts[value] / total, 4),
                    "evidence_count": total,
                }
            )

    for _, row in reviews.iterrows():
        for column, feature_type in REVIEW_FEATURE_COLUMNS.items():
            value = row[column]
            if value is None:
                continue
            rows.append(
                {
                    "feature_id": stable_id("review", row["review_id"], feature_type),
                    "place_id": row["place_id"],
                    "review_id": row["review_id"],
                    "feature_type": feature_type,
                    "value": value,
                    "source_id": "enaccess_reviews",
                    "confidence": 1.0,
                    "evidence_count": 1,
                }
            )
    return pd.DataFrame(rows)


def build_conflict_candidates(
    reviews: pd.DataFrame,
    *,
    half_life_days: float = 180.0,
    resolution_threshold: float = 0.60,
    high_quality_threshold: float = 0.75,
) -> pd.DataFrame:
    """Detect review conflicts and propose a recency-weighted provisional value.

    Place-level aggregates are deliberately excluded because they may summarize
    the same reviews and therefore are not independent evidence. Recency is
    measured relative to the latest dated review in each place-feature group,
    making the result deterministic for identical inputs.
    """
    if half_life_days <= 0:
        raise ValueError("half_life_days must be greater than zero")
    if not 0 <= resolution_threshold <= 1:
        raise ValueError("resolution_threshold must be between zero and one")
    if not resolution_threshold <= high_quality_threshold <= 1:
        raise ValueError("high_quality_threshold must be between resolution_threshold and one")

    evidence_rows: list[dict[str, object]] = []
    reviewed_at = pd.to_datetime(reviews["reviewed_at"], errors="coerce", utc=True, format="mixed")
    for index, review in reviews.iterrows():
        for review_column, feature_type in REVIEW_FEATURE_COLUMNS.items():
            value = review[review_column]
            if value not in {"yes", "no", "unsure"}:
                continue
            evidence_rows.append(
                {
                    "place_id": review["place_id"],
                    "review_id": review["review_id"],
                    "feature_type": feature_type,
                    "value": value,
                    "reviewed_at": reviewed_at.loc[index],
                }
            )

    if not evidence_rows:
        return pd.DataFrame(columns=CONFLICT_CANDIDATE_COLUMNS)

    evidence = pd.DataFrame(evidence_rows)
    rows: list[dict[str, object]] = []
    grouped = evidence.dropna(subset=["place_id", "feature_type"]).groupby(["place_id", "feature_type"])
    for (place_id, feature_type), group in grouped:
        counts = group["value"].value_counts(dropna=True).to_dict()
        yes_count = int(counts.get("yes", 0))
        no_count = int(counts.get("no", 0))
        unsure_count = int(counts.get("unsure", 0))
        if yes_count == 0 or no_count == 0:
            continue

        dated = group.dropna(subset=["reviewed_at"]).copy()
        latest_reviewed_at = dated["reviewed_at"].max() if not dated.empty else None
        if latest_reviewed_at is not None:
            age_days = (latest_reviewed_at - dated["reviewed_at"]).dt.total_seconds() / 86_400
            dated["recency_weight"] = 2 ** (-age_days / half_life_days)
            latest_review_ids = ";".join(
                sorted(dated.loc[dated["reviewed_at"] == latest_reviewed_at, "review_id"].astype(str))
            )
        else:
            dated["recency_weight"] = pd.Series(dtype=float)
            latest_review_ids = ""

        weights = dated.groupby("value")["recency_weight"].sum().to_dict()
        yes_weight = float(weights.get("yes", 0.0))
        no_weight = float(weights.get("no", 0.0))
        unsure_weight = float(weights.get("unsure", 0.0))
        weighted_decisive = yes_weight + no_weight
        weighted_total = weighted_decisive + unsure_weight
        dated_evidence_count = int(dated["value"].isin(["yes", "no"]).sum())
        temporal_coverage = dated_evidence_count / (yes_count + no_count)

        proposed_value = "unresolved"
        winner_share = 0.0
        if weighted_decisive > 0 and yes_weight != no_weight:
            proposed_value = "yes" if yes_weight > no_weight else "no"
            winner_share = max(yes_weight, no_weight) / weighted_decisive
        certainty = weighted_decisive / weighted_total if weighted_total > 0 else 0.0
        resolution_score = winner_share * temporal_coverage * certainty

        is_provisional = proposed_value != "unresolved" and resolution_score >= resolution_threshold
        if resolution_score >= high_quality_threshold:
            evidence_quality = "high"
        elif resolution_score >= resolution_threshold:
            evidence_quality = "medium"
        else:
            evidence_quality = "low"
        status = "provisional" if is_provisional else "human_review"
        notes = (
            f"Review-only recency weighting with a {half_life_days:g}-day half-life; "
            f"resolution threshold={resolution_threshold:.2f}. The score is heuristic and not calibrated."
        )
        rows.append(
            {
                "candidate_id": stable_id("conflict", place_id, feature_type),
                "place_id": place_id,
                "feature_type": feature_type,
                "conflict_type": "review_yes_no_disagreement",
                "yes_count": yes_count,
                "no_count": no_count,
                "unsure_count": unsure_count,
                "dated_evidence_count": dated_evidence_count,
                "latest_reviewed_at": latest_reviewed_at.isoformat() if latest_reviewed_at is not None else None,
                "latest_review_ids": latest_review_ids,
                "yes_weight": round(yes_weight, 6),
                "no_weight": round(no_weight, 6),
                "unsure_weight": round(unsure_weight, 6),
                "proposed_value": proposed_value,
                "resolution_method": "review_recency_weighted",
                "resolution_score": round(resolution_score, 6),
                "evidence_quality": evidence_quality,
                "status": status,
                "needs_human_review": int(not is_provisional),
                "notes": notes,
            }
        )
    return pd.DataFrame(rows, columns=CONFLICT_CANDIDATE_COLUMNS)


def build_walking_nodes(tactile_indicators: pd.DataFrame) -> pd.DataFrame:
    """Create initial walking network nodes from tactile indicator assets."""
    return pd.DataFrame(
        {
            "node_id": "tgsi_" + tactile_indicators["asset_id"].astype(str),
            "node_type": "tactile_indicator",
            "lat": tactile_indicators["lat"],
            "lng": tactile_indicators["lng"],
            "source_id": tactile_indicators["source_id"],
            "source_feature_id": tactile_indicators["asset_id"],
            "description": tactile_indicators["description"],
        }
    )


def empty_walking_edges() -> pd.DataFrame:
    """Return the placeholder edge table for the walking network workstream."""
    return pd.DataFrame(
        columns=[
            "edge_id",
            "from_node_id",
            "to_node_id",
            "distance_m",
            "accessibility_cost",
            "source_id",
            "notes",
        ]
    )

