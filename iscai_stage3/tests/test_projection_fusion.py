import unittest
from iscai_stage3.tracking.projection_fusion import *
from iscai_stage3.tracking.projection_mdht import ProjectionHoughConfig


class TestProjectionFusion(unittest.TestCase):
    def test_three_plane_and_fusion_recovers_line(self):
        detections=tuple(SpatiotemporalDetection(f"d{i}",i,10+0.5*i,20-0.25*i) for i in range(16))
        gate=SegmentGateConfig(minimum_common_support=8,minimum_distinct_frames=8,maximum_mean_residual_m=1.8,maximum_speed_mps=3)
        segments=and_fused_segments(detections,window_start=0,window_end=16,hough_config=ProjectionHoughConfig(peak_threshold_min=1),gate=gate)
        self.assertTrue(segments)
        self.assertAlmostEqual(segments[0].velocity_H0_mps[0],0.5,places=1)
        self.assertAlmostEqual(segments[0].velocity_H0_mps[1],-0.25,places=1)

    def test_invalid_plane_rejected(self):
        with self.assertRaises(ValueError):
            projection_points((SpatiotemporalDetection("d",0,0,0),),"oracle")

    def test_truth_identity_is_not_in_detection_contract(self):
        self.assertNotIn("track_id",SpatiotemporalDetection.__dataclass_fields__)
        self.assertNotIn("object_class",SpatiotemporalDetection.__dataclass_fields__)


if __name__ == "__main__": unittest.main()
