import unittest

from iscai_stage3.validation.synthetic_crossing import CrossingBenchmarkConfig, run_crossing_benchmark


class TestSyntheticCrossingBenchmark(unittest.TestCase):
    def test_report_is_reproducible_and_paired(self):
        config = CrossingBenchmarkConfig(trials=20, frames=9)
        self.assertEqual(run_crossing_benchmark(config), run_crossing_benchmark(config))

    def test_report_is_explicitly_synthetic(self):
        report = run_crossing_benchmark(CrossingBenchmarkConfig(trials=5, frames=5))
        self.assertTrue(report.synthetic_only)
        self.assertEqual(report.trials, 5)

    def test_invalid_probability_is_rejected(self):
        with self.assertRaises(ValueError):
            CrossingBenchmarkConfig(miss_probability=1.0)


if __name__ == "__main__":
    unittest.main()
