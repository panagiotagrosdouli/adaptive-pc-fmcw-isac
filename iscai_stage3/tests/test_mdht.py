import unittest
from iscai_stage3.tracking.cartesian import CartesianDetection, CartesianDetectionFrame
from iscai_stage3.tracking.mdht import MdhtConfig, fixed_bin_mdht, probabilistic_mdht

COV=((1,0,0),(0,1,0),(0,0,1))

class TestMdht(unittest.TestCase):
    def test_constant_velocity_produces_correct_peak(self):
        frames=tuple(CartesianDetectionFrame("s",i,float(i),(CartesianDetection(f"d{i}",(2.0+i,3.0+2*i,0.0),COV),)) for i in range(4))
        peak=fixed_bin_mdht(frames,config=MdhtConfig(position_bin_m=0.1,velocity_bin_mps=0.1))[0]
        self.assertEqual((peak.x0_m,peak.y0_m,peak.vx_mps,peak.vy_mps),(2.0,3.0,1.0,2.0))
        self.assertEqual(peak.votes,6)

    def test_no_oracle_fields_are_required(self):
        self.assertEqual(fixed_bin_mdht(()),())

    def test_noncausal_order_is_rejected(self):
        empty=lambda i,t: CartesianDetectionFrame("s",i,t,())
        with self.assertRaisesRegex(ValueError,"strictly increasing"):
            fixed_bin_mdht((empty(0,1.0),empty(1,1.0)))

    def test_probabilistic_peak_recovers_constant_velocity(self):
        frames=tuple(CartesianDetectionFrame("s",i,float(i),(CartesianDetection(f"d{i}",(2.0+i,3.0+2*i,0.0),COV),)) for i in range(4))
        peak=probabilistic_mdht(frames,config=MdhtConfig(position_bin_m=0.1,velocity_bin_mps=0.1))[0]
        self.assertEqual((peak.x0_m,peak.y0_m,peak.vx_mps,peak.vy_mps),(2.0,3.0,1.0,2.0))

    def test_each_detection_has_bounded_total_influence(self):
        frames=tuple(CartesianDetectionFrame("s",i,float(i),(CartesianDetection(f"d{i}",(float(i),0.0,0.0),COV),)) for i in range(3))
        peaks=probabilistic_mdht(frames,config=MdhtConfig(minimum_votes=1))
        self.assertAlmostEqual(sum(peak.normalized_score for peak in peaks),3.0)

    def test_negative_process_variance_is_rejected(self):
        with self.assertRaises(ValueError):
            probabilistic_mdht((),process_variance_m2=-1.0)

if __name__ == "__main__": unittest.main()
