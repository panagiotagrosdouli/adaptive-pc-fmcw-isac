import json
from pathlib import Path
import unittest


class TestPartAMdhtReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / "configs" / "part_a_mdht_reference.json"
        cls.config = json.loads(path.read_text(encoding="utf-8"))

    def test_reference_is_not_mislabeled_as_womd(self):
        self.assertEqual(self.config["semantics"], "part_a_simulated_trajectory_reference_not_womd")

    def test_linear_trajectory_matches_notebook(self):
        trajectory = self.config["trajectories"][0]
        t = 10.0
        x = sum(value * t**power for power, value in enumerate(trajectory["x"]))
        y = sum(value * t**power for power, value in enumerate(trajectory["y"]))
        self.assertAlmostEqual(x, 12.0 + 1.05 * t)
        self.assertAlmostEqual(y, 15.0 + 0.60 * t)

    def test_curved_trajectory_matches_notebook(self):
        trajectory = self.config["trajectories"][1]
        for t in (0.0, 12.0, 63.0):
            x = sum(value * t**power for power, value in enumerate(trajectory["x"]))
            y = sum(value * t**power for power, value in enumerate(trajectory["y"]))
            self.assertAlmostEqual(x, 18.0 + 0.95 * t)
            self.assertAlmostEqual(y, 60.0 - 0.45 * t + 0.015 * (t - 12.0) ** 2)

    def test_projection_and_acceptance_contract(self):
        self.assertEqual(self.config["projection_planes"], ["xy", "xt", "yt"])
        self.assertEqual(self.config["acceptance"]["expected_tracks"], 2)
        self.assertEqual(self.config["acceptance"]["maximum_false_tracks"], 0)


if __name__ == "__main__":
    unittest.main()
