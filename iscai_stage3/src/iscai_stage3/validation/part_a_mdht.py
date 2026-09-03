"""End-to-end continuity gate for the Part-A simulated MDHT scenario."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from iscai_stage3.tracking.projection_fusion import SpatiotemporalDetection, SegmentGateConfig, and_fused_segments
from iscai_stage3.tracking.projection_mdht import ProjectionHoughConfig
from iscai_stage3.tracking.rolling_mdht import StitchingConfig, stitch_segments, merge_duplicate_segments, track_points_by_frame


@dataclass(frozen=True)
class PartAMdhtReport:
    seed: int
    raw_segments: int
    merged_segments: int
    stitched_tracks: int
    accepted_tracks: int
    matched_labels: tuple[int, ...]
    false_tracks: int
    accepted: bool
    track_diagnostics: tuple[tuple[int, int, int, int], ...]
    semantics: str = "part_a_simulated_trajectory_reference_not_womd"


def run_part_a_reference(seed: int = 117290) -> PartAMdhtReport:
    frame_axis = np.arange(64, dtype=float)
    trajectories = (
        (12.0+1.05*frame_axis, 15.0+0.60*frame_axis, 1),
        (18.0+0.95*frame_axis, 60.0-0.45*frame_axis+0.015*(frame_axis-12.0)**2, 2),
    )
    rng = np.random.default_rng(seed)
    detections = []
    truth = {}
    next_id = 0
    for xs, ys, label in trajectories:
        for frame, x, y in zip(range(64), xs, ys):
            key=str(next_id); next_id+=1
            detections.append(SpatiotemporalDetection(key,frame,float(x+rng.normal(0,0.35)),float(y+rng.normal(0,0.35))))
            truth[key]=label
    for frame in range(64):
        for _ in range(4):
            key=str(next_id); next_id+=1
            detections.append(SpatiotemporalDetection(key,frame,float(rng.uniform(0,100)),float(rng.uniform(0,100))))
            truth[key]=0
    hough=ProjectionHoughConfig(rho_bound_mode="legacy_span")
    gate=SegmentGateConfig()
    merged=[]; raw_count=0
    for start in range(0,64-16+1,6):
        window=tuple(d for d in detections if start <= d.frame_index < start+16)
        raw=and_fused_segments(window,window_start=start,window_end=start+16,hough_config=hough,gate=gate)
        raw_count+=len(raw)
        merged.extend(merge_duplicate_segments(raw,window,0.45))
    tracks=stitch_segments(tuple(merged),StitchingConfig())
    accepted=[]; labels=[]; diagnostics=[]
    for track in tracks:
        points=track_points_by_frame(track)
        support=set().union(*(segment.support_ids for segment in track.segments))
        counts={label:sum(truth[key]==label for key in support) for label in (0,1,2)}
        diagnostics.append((len(track.segments),len(points),len(support),max(counts,key=counts.get)))
        if len(points)/64 < 0.90 or len(support) < 28 or len(track.segments) < 3:
            continue
        accepted.append(track)
        labels.append(max(counts,key=counts.get))
    false=sum(label==0 for label in labels)
    passed=len(accepted)==2 and false==0 and set(labels)=={1,2}
    return PartAMdhtReport(seed,raw_count,len(merged),len(tracks),len(accepted),tuple(labels),false,passed,tuple(diagnostics))
