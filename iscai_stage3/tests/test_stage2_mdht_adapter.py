import unittest
from iscai_stage3.tracking.cartesian import CartesianDetection, CartesianDetectionFrame
from iscai_stage3.tracking.stage2_mdht_adapter import cartesian_frames_to_mdht_cloud

COV=((1,0,0),(0,1,0),(0,0,1))


class TestStage2MdhtAdapter(unittest.TestCase):
    def test_unlabeled_frames_become_truth_free_cloud(self):
        frames=(
            CartesianDetectionFrame("s",4,0.4,(CartesianDetection("opaque-a",(1,2,0),COV),)),
            CartesianDetectionFrame("s",5,0.5,(CartesianDetection("opaque-b",(2,3,0),COV),)),
        )
        cloud=cartesian_frames_to_mdht_cloud(frames)
        self.assertTrue(cloud.truth_free)
        self.assertEqual(cloud.observation_frame,"H0")
        self.assertEqual(cloud.timestamps_s,(0.4,0.5))
        self.assertNotIn("track_id",repr(cloud))
        self.assertNotIn("object_class",repr(cloud))

    def test_mixed_scenarios_are_rejected(self):
        frames=(CartesianDetectionFrame("a",0,0.0,()),CartesianDetectionFrame("b",1,0.1,()))
        with self.assertRaisesRegex(ValueError,"one scenario"):
            cartesian_frames_to_mdht_cloud(frames)

    def test_noncausal_time_is_rejected(self):
        frames=(CartesianDetectionFrame("s",0,0.1,()),CartesianDetectionFrame("s",1,0.1,()))
        with self.assertRaisesRegex(ValueError,"strictly increasing"):
            cartesian_frames_to_mdht_cloud(frames)


if __name__ == "__main__": unittest.main()
