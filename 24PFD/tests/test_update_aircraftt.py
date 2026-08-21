"""Integration-ish tests for the aircraft-state update pipeline in main.py.

These exercise update_aircraftt end to end against ACdata, the same way real
upstream WebSocket frames drive it, without needing a live connection.
"""
import pytest

import main


@pytest.fixture(autouse=True)
def reset_acdata():
    # main.ACdata is module-level mutable state - reset it before each test
    # so tests don't leak aircraft between each other.
    main.ACdata = {}
    yield


def make_aircraft(heading=90, groundSpeed=200, altitude=1000, speed=None, onGround=False):
    payload = {
        "heading": heading,
        "groundSpeed": groundSpeed,
        "altitude": altitude,
        "isOnGround": onGround,
    }
    if speed is not None:
        payload["speed"] = speed
    return payload


class TestNewAircraftRegistration:
    def test_unknown_callsign_gets_default_state(self):
        content = {"TEST-1": make_aircraft()}
        main.update_aircraftt("d", content, 1.0)
        assert "TEST-1" in main.ACdata
        assert main.ACdata["TEST-1"]["roll"] == 0
        assert main.ACdata["TEST-1"]["pitch"] == 0

    def test_first_frame_does_not_compute_dynamics_yet(self):
        # First sighting only seeds new_aircraft_state(); real values land on
        # the *next* frame once there's a prev_* value to diff against.
        content = {"TEST-1": make_aircraft(groundSpeed=300, altitude=5000)}
        main.update_aircraftt("d", content, 1.0)
        assert main.ACdata["TEST-1"]["altitude"] == 0
        assert main.ACdata["TEST-1"]["groundSpeed"] == 0


class TestNonAircraftPayloadsIgnored:
    def test_non_dict_d_payload_is_skipped(self):
        # e.g. CONTROLLERS events reuse "d" for a list, not aircraft dict
        main.update_aircraftt("d", ["not", "aircraft", "data"], 1.0)
        assert main.ACdata == {}

    def test_non_dict_entries_within_content_are_skipped(self):
        content = {"robloxName": "someone", "TEST-1": make_aircraft()}
        main.update_aircraftt("d", content, 1.0)
        assert "robloxName" not in main.ACdata
        assert "TEST-1" in main.ACdata

    def test_wrong_datatype_key_is_ignored_entirely(self):
        main.update_aircraftt("s", {"TEST-1": make_aircraft()}, 1.0)
        assert main.ACdata == {}


class TestStaleAircraftRemoval:
    def test_aircraft_missing_from_new_frame_is_removed(self):
        main.update_aircraftt("d", {"TEST-1": make_aircraft()}, 1.0)
        assert "TEST-1" in main.ACdata
        main.update_aircraftt("d", {"TEST-2": make_aircraft()}, 1.0)
        assert "TEST-1" not in main.ACdata
        assert "TEST-2" in main.ACdata


class TestGroundSpeedVsIas:
    def test_ias_and_groundspeed_are_tracked_separately(self):
        # First frame: register
        main.update_aircraftt("d", {"TEST-1": make_aircraft(groundSpeed=150, speed=180, altitude=1000)}, 1.0)
        # Second frame: dynamics computed relative to first
        main.update_aircraftt("d", {"TEST-1": make_aircraft(groundSpeed=160, speed=190, altitude=1000)}, 1.0)
        ac = main.ACdata["TEST-1"]
        assert ac["groundSpeed"] == 160
        assert ac["ias"] == 190
        assert ac["groundSpeed"] != ac["ias"]

    def test_missing_speed_field_falls_back_to_groundspeed(self):
        # Upstream payload without "speed" (defensive: older/partial payloads)
        content = {"TEST-1": {"heading": 90, "groundSpeed": 140, "altitude": 1000, "isOnGround": False}}
        main.update_aircraftt("d", content, 1.0)
        main.update_aircraftt("d", content, 1.0)
        assert main.ACdata["TEST-1"]["ias"] == 140

    def test_bank_and_pitch_calcs_use_groundspeed_not_ias(self):
        # Two frames with a heading change; IAS is deliberately very different
        # from groundSpeed so any accidental use of IAS in bank/pitch would
        # produce a detectably different roll than the groundSpeed-only case.
        main.update_aircraftt("d", {"TEST-1": make_aircraft(heading=90, groundSpeed=200, speed=999, altitude=1000)}, 1.0)
        main.update_aircraftt("d", {"TEST-1": make_aircraft(heading=100, groundSpeed=200, speed=999, altitude=1000)}, 1.0)
        roll_with_high_ias = main.ACdata["TEST-1"]["roll"]

        main.ACdata = {}
        main.update_aircraftt("d", {"TEST-1": make_aircraft(heading=90, groundSpeed=200, speed=200, altitude=1000)}, 1.0)
        main.update_aircraftt("d", {"TEST-1": make_aircraft(heading=100, groundSpeed=200, speed=200, altitude=1000)}, 1.0)
        roll_with_matching_ias = main.ACdata["TEST-1"]["roll"]

        assert roll_with_high_ias == roll_with_matching_ias


class TestOnGroundSuppressesRoll:
    def test_turning_on_ground_produces_zero_roll(self):
        main.update_aircraftt("d", {"TEST-1": make_aircraft(heading=90, onGround=True)}, 1.0)
        main.update_aircraftt("d", {"TEST-1": make_aircraft(heading=150, onGround=True)}, 1.0)
        assert main.ACdata["TEST-1"]["roll"] == 0

    def test_same_turn_airborne_produces_nonzero_roll(self):
        main.update_aircraftt("d", {"TEST-1": make_aircraft(heading=90, groundSpeed=150, onGround=False)}, 1.0)
        main.update_aircraftt("d", {"TEST-1": make_aircraft(heading=150, groundSpeed=150, onGround=False)}, 1.0)
        assert main.ACdata["TEST-1"]["roll"] != 0

    def test_transition_from_airborne_to_ground_zeroes_roll_immediately(self):
        main.update_aircraftt("d", {"TEST-1": make_aircraft(heading=90, groundSpeed=150, onGround=False)}, 1.0)
        main.update_aircraftt("d", {"TEST-1": make_aircraft(heading=150, groundSpeed=150, onGround=False)}, 1.0)
        assert main.ACdata["TEST-1"]["roll"] != 0
        # Touches down mid-turn
        main.update_aircraftt("d", {"TEST-1": make_aircraft(heading=200, groundSpeed=20, onGround=True)}, 1.0)
        assert main.ACdata["TEST-1"]["roll"] == 0

    def test_onGround_defaults_false_when_field_missing(self):
        content = {"TEST-1": {"heading": 90, "groundSpeed": 150, "altitude": 1000}}
        main.update_aircraftt("d", content, 1.0)
        assert main.ACdata["TEST-1"]["onGround"] is False


class TestMalformedAircraftDoesNotCrashOthers:
    def test_one_broken_aircraft_does_not_stop_others_from_updating(self):
        content = {
            "GOOD-1": make_aircraft(heading=90, groundSpeed=200),
            "BAD-1": {"heading": 90},  # missing groundSpeed/altitude - should not blow up the loop
        }
        main.update_aircraftt("d", content, 1.0)
        main.update_aircraftt("d", content, 1.0)
        assert "GOOD-1" in main.ACdata
        assert main.ACdata["GOOD-1"]["groundSpeed"] == 200
