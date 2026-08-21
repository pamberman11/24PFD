"""Unit tests for the pure math helpers in main.py."""
import pytest

import main


class TestVerticalSpeedCalculation:
    def test_climbing(self):
        assert main.vertical_speed_calculation(1100, 1000, 1.0) == 100

    def test_descending(self):
        assert main.vertical_speed_calculation(900, 1000, 1.0) == -100

    def test_level(self):
        assert main.vertical_speed_calculation(1000, 1000, 1.0) == 0

    def test_scales_with_dt(self):
        # Same altitude delta over a longer interval means a smaller rate
        assert main.vertical_speed_calculation(1100, 1000, 2.0) == 50


class TestForwardSpeedFpsCalculation:
    def test_zero_speed(self):
        assert main.forward_speed_fps_calculation(0) == 0

    def test_positive_speed_is_positive_fps(self):
        result = main.forward_speed_fps_calculation(100)
        assert result > 0

    def test_known_conversion_factor(self):
        # groundSpeed -> studs/s -> fps, both fixed multipliers from the source
        gs = 120
        expected = gs * 0.5442765 * 1.8372
        assert main.forward_speed_fps_calculation(gs) == pytest.approx(expected)


class TestPitchAngleCalculation:
    def test_level_flight_is_zero_pitch(self):
        assert main.pitch_angle_calculation(0, 100) == 0

    def test_climbing_is_positive_pitch(self):
        pitch = main.pitch_angle_calculation(50, 100)
        assert pitch > 0

    def test_descending_is_negative_pitch(self):
        pitch = main.pitch_angle_calculation(-50, 100)
        assert pitch < 0

    def test_stationary_forward_speed_does_not_crash(self):
        # atan2 handles the 0/0 and x/0 cases gracefully - must not raise
        assert main.pitch_angle_calculation(0, 0) == 0
        pitch = main.pitch_angle_calculation(50, 0)
        assert pitch == 90  # straight up

    def test_45_degree_pitch(self):
        pitch = main.pitch_angle_calculation(100, 100)
        assert pitch == pytest.approx(45.0)


class TestBankAngle:
    def test_no_heading_change_is_zero_roll(self):
        assert main.bank_angle(90, 90, 1.0, 100) == 0

    def test_right_turn_is_positive_roll(self):
        # Heading increasing (e.g. 090 -> 100) is a right turn
        roll = main.bank_angle(100, 90, 1.0, 200)
        assert roll > 0

    def test_left_turn_is_negative_roll(self):
        # Heading decreasing (e.g. 090 -> 080) is a left turn
        roll = main.bank_angle(80, 90, 1.0, 200)
        assert roll < 0

    def test_wraps_across_north_as_shortest_path_right(self):
        # 350 -> 010 is a 20 degree right turn through North, not a 340 degree left turn
        roll_via_wrap = main.bank_angle(10, 350, 1.0, 200)
        roll_direct = main.bank_angle(20, 0, 1.0, 200)
        assert roll_via_wrap > 0
        assert roll_via_wrap == pytest.approx(roll_direct)

    def test_zero_speed_is_zero_roll(self):
        assert main.bank_angle(100, 90, 1.0, 0) == 0

    def test_faster_speed_increases_roll_for_same_turn_rate(self):
        slow = main.bank_angle(100, 90, 1.0, 50)
        fast = main.bank_angle(100, 90, 1.0, 300)
        assert fast > slow > 0
