import unittest
import numpy as np
from iscai_stage3.tracking.projection_mdht import *


class TestProjectionMdht(unittest.TestCase):
    def setUp(self):
        self.config=ProjectionHoughConfig(peak_threshold_fraction=0.4,peak_threshold_min=1.0)
        x=np.arange(20,dtype=float)
        self.points=np.column_stack((x,2.0*x+3.0))

    def test_accumulator_conserves_votes_per_theta(self):
        result=compute_projection_accumulator(self.points,self.config)
        np.testing.assert_allclose(np.sum(result.values,axis=0),len(self.points))

    def test_peak_supports_linear_points(self):
        raw=compute_projection_accumulator(self.points,self.config)
        smooth=ProjectionAccumulator(smooth_accumulator_3x3(raw.values),raw.rho_grid,raw.theta_grid_deg)
        peaks=detect_projection_peaks(smooth,self.config)
        supports=[supporting_point_ids(self.points,tuple(map(str,range(20))),p,self.config) for p in peaks]
        self.assertGreaterEqual(max(map(len,supports)),18)

    def test_nms_caps_peak_count(self):
        raw=compute_projection_accumulator(self.points,self.config)
        peaks=detect_projection_peaks(raw,self.config)
        self.assertLessEqual(len(peaks),self.config.max_peaks)

    def test_nonfinite_points_rejected(self):
        with self.assertRaises(ValueError):
            compute_projection_accumulator(np.array([[0.0,np.nan]]),self.config)

    def test_legacy_mode_is_explicit(self):
        legacy=ProjectionHoughConfig(rho_bound_mode="legacy_span")
        self.assertEqual(legacy.rho_bound_mode,"legacy_span")


if __name__ == "__main__": unittest.main()
