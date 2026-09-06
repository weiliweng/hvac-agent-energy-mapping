"""Deterministic mapping and data-quality logic."""

from __future__ import annotations

import re
from collections import Counter

import pandas as pd


NULL_TAGS = {"", "nan", "none", "null", "n/a", "na"}
POINT_ID_RE = re.compile(r"^(VAV|PIU)_(\d+)_(\d+)(?:_|$)", re.IGNORECASE)
EQUIPMENT_RE = re.compile(r"^PIU-(\d{2})-(\d{2})$", re.IGNORECASE)


def normalize_tags(value: object) -> list[str]:
    if pd.isna(value):
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in str(value).split(","):
        tag = re.sub(r"\s+", " ", raw.strip())
        key = tag.casefold()
        if key in NULL_TAGS or key in seen:
            continue
        normalized.append(tag)
        seen.add(key)
    return normalized


def _tag_number(tags: list[str], name: str) -> int | None:
    pattern = re.compile(rf"^{re.escape(name)}\s*:\s*(\d+)\s*$", re.IGNORECASE)
    values = {int(match.group(1)) for tag in tags if (match := pattern.match(tag))}
    return next(iter(values)) if len(values) == 1 else None


def parse_point_identifier(value: object) -> tuple[str | None, int | None, int | None]:
    match = POINT_ID_RE.match(str(value).strip())
    if not match:
        return None, None, None
    return match.group(1).upper(), int(match.group(2)), int(match.group(3))


def validate_schedule(schedule: pd.DataFrame) -> dict[tuple[int, int], str]:
    required = {"equipment_ref", "floor", "unit_number"}
    if not required.issubset(schedule.columns):
        raise ValueError(f"Schedule requires columns: {sorted(required)}")
    if schedule["equipment_ref"].duplicated().any():
        raise ValueError("Schedule contains duplicate equipment_ref values")
    index: dict[tuple[int, int], str] = {}
    for row in schedule.itertuples(index=False):
        match = EQUIPMENT_RE.match(str(row.equipment_ref))
        if not match:
            raise ValueError(f"Invalid equipment reference: {row.equipment_ref}")
        encoded = (int(match.group(1)), int(match.group(2)))
        columns = (int(row.floor), int(row.unit_number))
        if encoded != columns:
            raise ValueError(f"Equipment reference conflicts with floor/unit columns: {row.equipment_ref}")
        index[columns] = str(row.equipment_ref).upper()
    return index


def map_inventory(points: pd.DataFrame, schedule: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    required = {"point_name", "tagged_result"}
    if not required.issubset(points.columns):
        raise ValueError(f"Point inventory requires columns: {sorted(required)}")
    schedule_index = validate_schedule(schedule)
    result = points.loc[:, ["point_name", "tagged_result"]].copy()
    result.insert(0, "source_row", range(2, len(result) + 2))
    result["point_name"] = result["point_name"].fillna("").astype(str).str.strip()
    result["tag_list"] = result["tagged_result"].map(normalize_tags)
    result["normalized_tags"] = result["tag_list"].map(lambda tags: ", ".join(tags))
    parsed = result["point_name"].map(parse_point_identifier)
    result[["id_family", "id_floor", "id_unit"]] = pd.DataFrame(parsed.tolist(), index=result.index)
    result["tag_floor"] = result["tag_list"].map(lambda tags: _tag_number(tags, "floorNum"))
    result["tag_zone"] = result["tag_list"].map(lambda tags: _tag_number(tags, "zone"))
    result["missing_tags"] = result["tag_list"].map(len).eq(0)
    result["duplicate_record"] = result.duplicated(["point_name", "normalized_tags"], keep=False)
    result["floor_disagreement"] = result["id_floor"].notna() & result["tag_floor"].notna() & result["id_floor"].ne(result["tag_floor"])
    result["unit_disagreement"] = result["id_unit"].notna() & result["tag_zone"].notna() & result["id_unit"].ne(result["tag_zone"])

    def decide(row: pd.Series) -> tuple[str, str, str]:
        if row.id_family not in {"VAV", "PIU"}:
            return "", "not_applicable", "identifier is not a VAV/PIU point"
        if row.floor_disagreement or row.unit_disagreement:
            return "", "review", "identifier conflicts with location tags"
        candidate = schedule_index.get((int(row.id_floor), int(row.id_unit)))
        if candidate is None:
            return "", "abstain", "no exact floor-unit entry in schedule"
        return candidate, "mapped_high_confidence", "exact floor-unit identifier match"

    decisions = result.apply(decide, axis=1, result_type="expand")
    decisions.columns = ["equipment_ref", "mapping_status", "mapping_reason"]
    result = pd.concat([result, decisions], axis=1)
    statuses = Counter(result.mapping_status)
    covered = result.loc[result.mapping_status.eq("mapped_high_confidence"), "equipment_ref"].nunique()
    metrics = {
        "source_rows": int(len(result)),
        "schedule_equipment": int(len(schedule)),
        "missing_tag_rows": int(result.missing_tags.sum()),
        "duplicate_rows": int(result.duplicate_record.sum()),
        "floor_disagreements": int(result.floor_disagreement.sum()),
        "unit_disagreements": int(result.unit_disagreement.sum()),
        "mapping_status_counts": dict(sorted(statuses.items())),
        "covered_equipment": int(covered),
        "schedule_coverage": covered / len(schedule) if len(schedule) else None,
    }
    return result.drop(columns=["tag_list"]), metrics
