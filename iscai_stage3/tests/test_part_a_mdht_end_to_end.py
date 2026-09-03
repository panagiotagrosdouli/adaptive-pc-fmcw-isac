import unittest
from iscai_stage3.validation.part_a_mdht import run_part_a_reference


class TestPartAMdhtEndToEnd(unittest.TestCase):
    def test_reference_is_reproducible(self):
        self.assertEqual(run_part_a_reference(),run_part_a_reference())

    def test_semantics_are_not_womd(self):
        self.assertEqual(run_part_a_reference().semantics,"part_a_simulated_trajectory_reference_not_womd")

    def test_part_a_acceptance_contract_passes(self):
        report=run_part_a_reference()
        self.assertTrue(report.accepted)
        self.assertEqual(report.accepted_tracks,2)
        self.assertEqual(set(report.matched_labels),{1,2})
        self.assertEqual(report.false_tracks,0)


if __name__ == "__main__": unittest.main()
