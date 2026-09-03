import unittest
from iscai_stage3.tracking.projection_fusion import MdhtSegment, SpatiotemporalDetection
from iscai_stage3.tracking.rolling_mdht import *


def segment(start, offset=0.0, prefix="a"):
    frames=tuple(range(start,start+8))
    positions=tuple((offset+0.5*f,2.0+0.2*f) for f in frames)
    return MdhtSegment(start,start+8,frozenset(f"{prefix}{f}" for f in frames),frames,positions,(0.5,0.2),0.1)


class TestRollingMdht(unittest.TestCase):
    def test_overlapping_segments_are_stitched(self):
        tracks=stitch_segments((segment(0),segment(6,prefix="b")))
        self.assertEqual(len(tracks),1)
        self.assertEqual(len(tracks[0].segments),2)

    def test_distinct_motion_starts_new_track(self):
        tracks=stitch_segments((segment(0),segment(6,offset=50,prefix="b")))
        self.assertEqual(len(tracks),2)

    def test_duplicate_suppression_uses_support_jaccard(self):
        original=segment(0)
        duplicate=MdhtSegment(0,8,original.support_ids,original.frame_indices,original.positions_H0_m,original.velocity_H0_mps,0.2)
        kept=suppress_duplicate_segments((duplicate,original),0.45)
        self.assertEqual(kept,(original,))

    def test_stitching_is_deterministic(self):
        values=(segment(6,prefix="b"),segment(0))
        self.assertEqual(stitch_segments(values),stitch_segments(tuple(reversed(values))))

    def test_part_a_merge_unions_support(self):
        original=segment(0)
        extra=MdhtSegment(0,8,frozenset(set(original.support_ids)|{"extra"}),original.frame_indices,original.positions_H0_m,original.velocity_H0_mps,0.2)
        detections=tuple(SpatiotemporalDetection(f"a{i}",i,0.5*i,2+0.2*i) for i in range(8))+(SpatiotemporalDetection("extra",0,0,2),)
        merged=merge_duplicate_segments((original,extra),detections,0.45)
        self.assertIn("extra",merged[0].support_ids)


if __name__ == "__main__": unittest.main()
