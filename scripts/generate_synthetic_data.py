#!/usr/bin/env python3
"""Generate deterministic synthetic fixtures; never reads private project files."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "synthetic"


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    equipment = []
    for floor, units in [(1, 4), (2, 4), (3, 3)]:
        for unit in range(1, units + 1):
            equipment.append({
                "equipment_ref": f"PIU-{floor:02d}-{unit:02d}", "floor": floor,
                "unit_number": unit, "room_served": f"RM {floor}{unit:03d}",
                "max_flow_cfm": 600 if unit < 4 else 1200,
            })

    points = []
    suffixes = [
        ("SpaceTemp", "temp, sensor"),
        ("EffOccHeatSetpt", "heating, sp"),
        ("EffOccCoolSetpt", "cooling, sp"),
    ]
    for item in equipment:
        family = "PIU" if item["unit_number"] % 2 == 0 else "VAV"
        for suffix, semantic in suffixes:
            points.append({
                "point_name": f"{family}_{item['floor']}_{item['unit_number']}_{suffix}",
                "tagged_result": f"{family.lower()}, variableAirVolume, floorNum: {item['floor']}, zone: {item['unit_number']}, {semantic}",
            })
    for floor, unit in [(4, 1), (4, 2), (5, 1), (2, 9)]:
        for suffix, semantic in suffixes:
            points.append({"point_name": f"VAV_{floor}_{unit}_{suffix}", "tagged_result": f"vav, floorNum: {floor}, zone: {unit}, {semantic}"})
    points.extend([
        {"point_name": "PIU_2_3_SpaceTemp", "tagged_result": "piu, floorNum: 3, zone: 3, temp, sensor"},
        {"point_name": "VAV_1_4_EffOccCoolSetpt", "tagged_result": "vav, floorNum: 1, zone: 9, cooling, sp"},
        {"point_name": "AHU_1_SupplyAirTemp", "tagged_result": "ahu, supply, air, temp, sensor"},
        {"point_name": "Boiler_Enable", "tagged_result": "boiler, enable, cmd"},
        {"point_name": "Weather_OAT", "tagged_result": "weather, outside, air, temp, sensor"},
        {"point_name": "VAV_6_1_Unknown", "tagged_result": "nan"},
    ])
    points.append(dict(points[0]))
    write_csv(OUT / "equipment_schedule.csv", equipment)
    write_csv(OUT / "bas_points.csv", points)
    print(f"Generated {len(equipment)} equipment rows and {len(points)} point rows")


if __name__ == "__main__":
    main()
