import pandas as pd
import unittest

from hvac_mapping.evaluation import evaluate_labels
from hvac_mapping.pipeline import map_inventory, normalize_tags, parse_point_identifier, validate_schedule


def schedule():
    return pd.DataFrame({"equipment_ref": ["PIU-03-07"], "floor": [3], "unit_number": [7]})


class PipelineTests(unittest.TestCase):
    def test_tag_normalization_removes_nulls_and_duplicates(self):
        self.assertEqual(normalize_tags("vav, nan, VAV, floorNum: 3"), ["vav", "floorNum: 3"])

    def test_identifier_parser(self):
        self.assertEqual(parse_point_identifier("VAV_9_2_EffOccCoolSetpt"), ("VAV", 9, 2))

    def test_exact_match_and_unsupported_floor_abstention(self):
        points = pd.DataFrame({
            "point_name": ["PIU_3_7_SpaceTemp", "VAV_9_2_EffOccCoolSetpt"],
            "tagged_result": ["piu, floorNum: 3, zone: 7", "vav, floorNum: 9, zone: 2"],
        })
        result, _ = map_inventory(points, schedule())
        self.assertEqual(result.loc[0, "equipment_ref"], "PIU-03-07")
        self.assertEqual(result.loc[0, "mapping_status"], "mapped_high_confidence")
        self.assertEqual(result.loc[1, "mapping_status"], "abstain")

    def test_conflicting_tag_routes_to_review(self):
        points = pd.DataFrame({"point_name": ["PIU_3_7_SpaceTemp"], "tagged_result": ["piu, floorNum: 4, zone: 7"]})
        result, _ = map_inventory(points, schedule())
        self.assertEqual(result.loc[0, "mapping_status"], "review")

    def test_schedule_validation_fails_closed(self):
        bad = pd.DataFrame({"equipment_ref": ["PIU-03-07"], "floor": [7], "unit_number": [3]})
        with self.assertRaises(ValueError):
            validate_schedule(bad)

    def test_human_evaluation_metrics(self):
        labels = pd.DataFrame({"reviewer_decision": ["correct_as_predicted", "incorrect_mapping", "valid_abstention", "missed_mapping", ""]})
        metrics = evaluate_labels(labels)
        self.assertEqual(metrics["reviewed"], 4)
        self.assertEqual(metrics["selective_precision"], 0.5)
        self.assertEqual(metrics["abstention_validity"], 0.5)
        self.assertEqual(metrics["overall_decision_accuracy"], 0.5)


if __name__ == "__main__":
    unittest.main()
