import math
import random
import unittest
from fractions import Fraction as Q

from perfectjet.applications.nfl_scouting.crossing import (
    travel_time, travel_time_bounds, los_confounding_receipt, extract_crossing)
from perfectjet.applications.nfl_scouting.schema import Frame, Attempt


def trajectory(onset=0.2, acceleration=4.0, initial_speed=0.0, step=0.1):
    frames=[]
    for i in range(-5, 26):
        t=round(i*step, 10)
        dt=max(0.0, t-onset)
        frames.append(Frame(t, initial_speed*dt+0.5*acceleration*dt*dt, 0.0))
    return frames


class TravelTimeTests(unittest.TestCase):
    def test_positive_root_replays_distance_and_handles_zero(self):
        for d,v,a in ((1,0,2),(4,3,2),(0.001,50,0.01),(3,0.4,20)):
            t=travel_time(d,v,a)
            self.assertAlmostEqual(v*t+a*t*t/2,d,12)
            self.assertGreater(t,0)
        self.assertEqual(travel_time(0,0,1),0)

    def test_stable_when_subtractive_formula_loses_small_time(self):
        t=travel_time(1,1e16,1)
        self.assertAlmostEqual(t,1e-16,30)
        self.assertEqual((math.sqrt(1e32+2)-1e16),0)

    def test_large_discriminant_does_not_overflow_a_finite_root(self):
        self.assertAlmostEqual(travel_time(1e308,1e308,1e308),math.sqrt(3)-1,15)

    def test_monotone_box_encloses_many_interior_models(self):
        box=travel_time_bounds((0.5,3),(0,4),(0.2,8));rng=random.Random(21)
        for _ in range(250):
            t=travel_time(rng.uniform(0.5,3),rng.uniform(0,4),rng.uniform(0.2,8))
            self.assertLessEqual(box['lower'],t)
            self.assertLessEqual(t,box['upper'])
        self.assertTrue(box['endpoint_polynomial_signs_checked_exactly'])

    def test_endpoint_brackets_have_exact_polynomial_signs(self):
        b=travel_time_bounds((1,1),(0.3,0.3),(2.7,2.7))
        d,v,a=map(Q.from_float,(1.0,0.3,2.7))
        def residual(t):
            t=Q.from_float(t)
            return a*t*t+2*v*t-2*d
        self.assertLessEqual(residual(b['lower']),0)
        self.assertGreaterEqual(residual(b['upper']),0)

    def test_invalid_or_impossible_domains_are_rejected(self):
        for args in ((-1,0,1),(1,-1,1),(1,0,0),(1,0,-1),(math.nan,0,1)):
            with self.assertRaises(ValueError):travel_time(*args)
        for box in (((2,1),(0,1),(1,2)),((1,2),(-1,1),(1,2)),((1,2),(0,1),(0,2))):
            with self.assertRaises(ValueError):travel_time_bounds(*box)

    def test_exact_confounding_witness_and_nonlinear_counterexample(self):
        r=los_confounding_receipt()
        self.assertFalse(r['onset_identification']['identified'])
        self.assertFalse(r['travel_identification']['identified'])
        first,second=r['nonlinear_explanations']
        self.assertEqual(first['snap_to_los'],second['snap_to_los'])
        self.assertNotEqual(first['onset'],second['onset'])
        self.assertNotEqual(first['acceleration'],second['acceleration'])
        self.assertTrue(r['identities_replayed'])


class CrossingExtractionTests(unittest.TestCase):
    def test_constant_acceleration_decomposition_and_fixed_horizon(self):
        r=extract_crossing(trajectory(),0,1.28)
        self.assertTrue(r['usable']);self.assertTrue(r['usable_for_post_snap_onset'])
        # Threshold onset is a tracking proxy, not the analytic physiological onset.
        self.assertAlmostEqual(r['motion_onset_time'],0.3)
        self.assertAlmostEqual(r['snap_to_los'],1.0)
        self.assertAlmostEqual(r['motion_to_los'],0.7)
        self.assertAlmostEqual(r['post_onset_displacement'],0.70)
        self.assertLess(r['reconstruction_identity_error'],1e-12)
        self.assertFalse(r['reaction_time_interpretation'])

    def test_attempt_input_translation_rotation_and_reflection(self):
        frames=trajectory();base=extract_crossing(frames,0,1.28)
        translated=[Frame(f.t,f.x+100,f.y-20) for f in frames]
        rotated=[Frame(f.t,-f.y+10,f.x-8) for f in frames]
        reflected=[Frame(f.t,-f.x,f.y) for f in frames]
        cases=[extract_crossing(Attempt('a','p','NFL',translated,'2024-09-01'),0,1.28),
               extract_crossing(rotated,0,1.28,axis=(0,1)),
               extract_crossing(reflected,0,1.28,direction=-1)]
        for r in cases:
            self.assertTrue(r['usable'])
            self.assertAlmostEqual(r['snap_to_los'],base['snap_to_los'])
            self.assertAlmostEqual(r['post_onset_displacement'],base['post_onset_displacement'])

    def test_anticipation_is_preserved_and_not_called_reaction(self):
        r=extract_crossing(trajectory(onset=-0.2,initial_speed=1),0,1)
        self.assertTrue(r['anticipation_or_moving_at_snap'])
        self.assertLessEqual(r['onset_delay'],0)
        self.assertFalse(r['usable_for_post_snap_onset'])
        self.assertIn('onset_at_or_before_snap',r['flags'])
        self.assertFalse(r['reaction_time_interpretation'])
        if r['usable']:self.assertLess(r['reconstruction_identity_error'],1e-12)

    def test_already_moving_window_has_censored_onset_but_observed_crossing(self):
        frames=[Frame(i/10,2*i/10,0) for i in range(-5,26)]
        result=extract_crossing(frames,0,1)
        self.assertFalse(result['usable'])
        self.assertIn('onset_left_censored',result['flags'])
        self.assertIsNone(result['motion_onset_time'])
        self.assertIsNone(result['motion_to_los'])
        self.assertAlmostEqual(result['snap_to_los'],0.5)
        self.assertTrue(result['anticipation_or_moving_at_snap'])
        self.assertFalse(result['reaction_time_interpretation'])

    def test_missing_crossing_interval_is_flagged(self):
        frames=[f for f in trajectory() if f.t not in (0.9,1.0)]
        r=extract_crossing(frames,0,1.28)
        self.assertFalse(r['usable'])
        self.assertIn('crossing_in_missing_interval',r['flags'])

    def test_irregular_times_and_unobserved_crossing_are_flagged(self):
        frames=trajectory();frames[5]=Frame(frames[4].t,frames[5].x,0)
        r=extract_crossing(frames,0,1)
        self.assertIn('nonincreasing_frame_times',r['flags'])
        r=extract_crossing(trajectory(),0,100)
        self.assertFalse(r['usable']);self.assertIn('los_crossing_not_observed',r['flags'])
        r=extract_crossing(trajectory(),0,1.28,maximum_post_snap=0.95)
        self.assertIn('los_crossing_not_observed',r['flags'])

    def test_low_position_noise_does_not_create_false_reaction_claim(self):
        rng=random.Random(22)
        frames=[Frame(f.t,f.x+rng.uniform(-0.002,0.002),f.y) for f in trajectory()]
        r=extract_crossing(frames,0,1.28)
        self.assertTrue(r['usable'])
        self.assertLess(abs(r['snap_to_los']-1),0.01)
        self.assertFalse(r['reaction_time_interpretation'])

    def test_meaningful_recrossing_is_rejected(self):
        frames=trajectory()
        frames=[Frame(f.t,0.5 if f.t>=1.4 else f.x,f.y) for f in frames]
        r=extract_crossing(frames,0,1.28)
        self.assertFalse(r['usable']);self.assertIn('significant_los_recrossing',r['flags'])

    def test_snap_and_post_onset_horizon_must_be_observed(self):
        self.assertIn('snap_outside_tracking',extract_crossing(trajectory(),-2,1)['flags'])
        r=extract_crossing([f for f in trajectory() if f.t<=0.6],0,0.1)
        self.assertIn('post_onset_horizon_unobserved',r['flags']);self.assertFalse(r['usable'])


if __name__=='__main__':unittest.main()
