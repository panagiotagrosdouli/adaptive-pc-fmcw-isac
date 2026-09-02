import unittest
from pathlib import Path

from iscai_stage1.config import load_stage1_config


class TestStage1Config(unittest.TestCase):
    def test_repository_config_matches_frozen_contract(self) -> None:
        config_path = (
            Path(__file__).resolve().parents[1]
            / "configs"
            / "stage1.json"
        )
        config = load_stage1_config(config_path)

        self.assertEqual(config.schema_version, 1)
        self.assertEqual(
            config.artifact_semantics,
            "causal_womd_annotation_upstream",
        )
        self.assertEqual(
            config.headlamp.translation_in_sdc_m(4.8),
            (2.4, 0.0, 0.0),
        )
        self.assertEqual(config.receiver.mode, "centroid_baseline")


if __name__ == "__main__":
    unittest.main()
