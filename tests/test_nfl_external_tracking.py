import numpy as np
import unittest

from perfectjet.applications.nfl_scouting.external_tracking import (
    causal_velocity_sequence, defensive_geometry, directional_interval, first_passage, relative_frame_clock,
    is_pass_rush_role,
    history_extrapolation,
)
from perfectjet.applications.nfl_scouting.schema import Frame



class ExternalTrackingTests(unittest.TestCase):
    def test_defense_metadata_geometry_and_no_absolute_flip(self):
        assert defensive_geometry("right",43,44)==(-1.0,1.0)
        assert defensive_geometry("left",76,75)==(1.0,1.0)
        with self.assertRaisesRegex(ValueError,"defensive side"):
            defensive_geometry("right",43,42)


    def test_causal_velocity_prefix_unaffected_by_future(self):
        frames=[Frame(i/10,(i/10)**2,i/100) for i in range(15)]
        before=causal_velocity_sequence("1","a",frames)
        frames[-1].x=10000
        after=causal_velocity_sequence("1","a",frames)
        assert before.channels[:-1]==after.channels[:-1]
        assert before.channels[-1]!=after.channels[-1]


    def test_missing_intervals_are_not_interpolated_into_velocity(self):
        frames=[Frame(i/10,i/10,0) for i in range(15) if i!=7]
        with self.assertRaisesRegex(ValueError,"nonuniform"):
            causal_velocity_sequence("1","a",frames)


    def test_forward_progress_does_not_count_lateral_arc(self):
        frames=[Frame(i/10,0,i/10) for i in range(11)]
        result=directional_interval(frames,0.2)
        assert result['forward_displacement_05']==0
        assert np.isclose(result['path_arc_05'],0.5)
        assert result['forward_path_fraction_05']==0


    def test_first_passage_interpolates_and_retains_censoring(self):
        frames=[Frame(i/10,i/5,0) for i in range(11)]
        assert np.isclose(first_passage(frames,0.55),0.275)
        assert first_passage(frames,3) is None


    def test_directional_interval_rejects_gap(self):
        frames=[Frame(i/10,i/10,0) for i in range(11) if i in (0,1,2,7,8,9,10)]
        assert directional_interval(frames,0.2) is None


    def test_whole_second_clock_does_not_collapse_distinct_frames(self):
        times=["2021-09-10T00:26:31Z"]*9+["2021-09-10T00:26:32Z"]*10
        relative,kind=relative_frame_clock(range(1,20),times,6)
        assert kind=="whole_second_quantized"
        assert np.isclose(relative[0],-.5)
        assert np.isclose(relative[9],.4)
        assert np.allclose(np.diff(relative),.1)


    def test_frame_clock_detects_inconsistent_sampling(self):
        times=["2021-09-10T00:26:31Z"]*5+["2021-09-10T00:26:34Z"]*5
        with self.assertRaisesRegex(ValueError,"disagree"):
            relative_frame_clock(range(1,11),times,6)


    def test_real_role_capitalization_differs_from_source_prose(self):
        assert is_pass_rush_role("Pass Rush")
        assert is_pass_rush_role("Pass rush")
        assert not is_pass_rush_role("Pass Route")


    def test_time_polynomial_forecast_reproduces_linear_past_trend(self):
        times=np.arange(-4,1)*.1
        past=np.column_stack([2+3*times,1-2*times])
        future=np.arange(1,4)*.1
        assert np.allclose(history_extrapolation(past),np.column_stack([2+3*future,1-2*future]))
