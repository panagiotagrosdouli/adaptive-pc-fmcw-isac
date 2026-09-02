import math
import unittest

from iscai_stage1.geometry.rigid import RigidTransform
from iscai_stage2.observations.contracts import MeasurementCovariance
from iscai_stage2.observations.detection_set import UnlabeledDetection, UnlabeledDetectionFrame
from iscai_stage3.tracking.cartesian import detection_frame_to_H0
from iscai_stage3.tracking.gnn import build_gnn_tracklets


def frame(index, timestamp, range_m, azimuth=0.0):
    covariance = MeasurementCovariance(matrix=((0.04,0,0,0),(0,0.25,0,0),(0,0,0.01,0),(0,0,0,0.0025)))
    return UnlabeledDetectionFrame("scenario", index, timestamp, (UnlabeledDetection(f"d{index}", range_m, 0.0, azimuth, 0.0, covariance),))


class TestTruthFreeTracking(unittest.TestCase):
    def setUp(self):
        self.identity = RigidTransform(rotation=((1,0,0),(0,1,0),(0,0,1)), translation=(0,0,0))

    def test_angular_covariance_is_propagated(self):
        converted = detection_frame_to_H0(frame(0, 0.0, 10.0), T_H0_from_Ht=self.identity)
        covariance = converted.detections[0].covariance_H0_m2
        self.assertAlmostEqual(covariance[0][0], 0.04)
        self.assertAlmostEqual(covariance[1][1], 1.0)
        self.assertAlmostEqual(covariance[2][2], 0.25)

    def test_dynamic_frame_is_transformed_before_tracking(self):
        moved = RigidTransform(rotation=((1,0,0),(0,1,0),(0,0,1)), translation=(1,0,0))
        a = detection_frame_to_H0(frame(0, 0.0, 10.0), T_H0_from_Ht=self.identity)
        b = detection_frame_to_H0(frame(1, 0.1, 9.0), T_H0_from_Ht=moved)
        tracks = build_gnn_tracklets((a, b))
        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0].positions_H0_m[0], tracks[0].positions_H0_m[1])

    def test_noncausal_frame_order_is_rejected(self):
        a = detection_frame_to_H0(frame(0, 0.1, 10.0), T_H0_from_Ht=self.identity)
        b = detection_frame_to_H0(frame(1, 0.1, 10.0), T_H0_from_Ht=self.identity)
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            build_gnn_tracklets((a, b))

    def test_tracking_contract_contains_no_oracle_identity(self):
        converted = detection_frame_to_H0(frame(0, 0.0, 10.0), T_H0_from_Ht=self.identity)
        self.assertNotIn("track_id", repr(converted))
        self.assertNotIn("object_class", repr(converted))


if __name__ == "__main__":
    unittest.main()
