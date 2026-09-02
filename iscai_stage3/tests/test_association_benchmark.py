import unittest

from iscai_stage3.tracking.cartesian import CartesianDetection, CartesianDetectionFrame
from iscai_stage3.validation.association_benchmark import evaluate_gnn_association


COVARIANCE = ((0.25, 0.0, 0.0), (0.0, 0.25, 0.0), (0.0, 0.0, 0.25))


def detection(key, x, y=0.0, covariance=COVARIANCE):
    return CartesianDetection(key, (x, y, 0.0), covariance)


class TestAssociationBenchmark(unittest.TestCase):
    def test_truth_is_used_only_by_evaluator(self):
        frames = (
            CartesianDetectionFrame("s", 0, 0.0, (detection("a0", 0.0),)),
            CartesianDetectionFrame("s", 1, 0.1, (detection("a1", 0.1),)),
        )
        result = evaluate_gnn_association(
            frames,
            evaluator_identity_by_detection_key={"a0": "A", "a1": "A"},
            association_metric="mahalanobis",
        )
        self.assertEqual(result.association_accuracy, 1.0)
        self.assertNotIn("A", repr(frames))

    def test_unknown_metric_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown association metric"):
            evaluate_gnn_association(
                (CartesianDetectionFrame("s", 0, 0.0, ()),),
                evaluator_identity_by_detection_key={},
                association_metric="oracle",
            )

    def test_covariance_can_change_assignment_ranking(self):
        small = ((0.01,0,0),(0,0.01,0),(0,0,0.01))
        large_y = ((0.01,0,0),(0,100.0,0),(0,0,0.01))
        frames = (
            CartesianDetectionFrame("s", 0, 0.0, (
                detection("a0", 0.0, 0.0, small),
                detection("b0", 0.0, 3.0, large_y),
            )),
            CartesianDetectionFrame("s", 1, 0.1, (
                detection("a1", 0.0, 1.4, large_y),
                detection("b1", 0.0, 1.6, small),
            )),
        )
        truth = {"a0":"A","a1":"A","b0":"B","b1":"B"}
        euclidean = evaluate_gnn_association(
            frames, evaluator_identity_by_detection_key=truth,
            association_metric="euclidean", euclidean_gate_m=10.0,
        )
        covariance = evaluate_gnn_association(
            frames, evaluator_identity_by_detection_key=truth,
            association_metric="mahalanobis", chi_square_gate=1000.0,
        )
        self.assertNotEqual(euclidean.correct_edges, covariance.correct_edges)


if __name__ == "__main__":
    unittest.main()
