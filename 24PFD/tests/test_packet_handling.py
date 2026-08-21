import json

import pytest

import main


@pytest.fixture(autouse=True)
def reset_state():
    main.ACdata = {}
    main.last_update_time = 0
    yield


class TestRemoveNonAircraftEntries:
    def test_removes_callsigns_absent_from_new_content(self):
        acdata = {"A": {}, "B": {}}
        content = {"A": {"heading": 1}}
        main.remove_non_aircraft_entries(acdata, content)
        assert list(acdata.keys()) == ["A"]

    def test_keeps_all_when_all_still_present(self):
        acdata = {"A": {}, "B": {}}
        content = {"A": {"heading": 1}, "B": {"heading": 2}}
        main.remove_non_aircraft_entries(acdata, content)
        assert set(acdata.keys()) == {"A", "B"}

    def test_non_dict_content_values_do_not_count_as_active(self):
        acdata = {"A": {}}
        content = {"A": "not-a-dict"}
        main.remove_non_aircraft_entries(acdata, content)
        assert acdata == {}

    def test_empty_content_clears_everything(self):
        acdata = {"A": {}, "B": {}}
        main.remove_non_aircraft_entries(acdata, {})
        assert acdata == {}


class TestHandlePacketRateLimiting:
    def test_first_packet_is_always_processed(self):
        raw = json.dumps({"d": {"TEST-1": {"heading": 1, "groundSpeed": 1, "altitude": 1, "isOnGround": False}}})
        main.handle_packet(raw)
        assert "TEST-1" in main.ACdata

    def test_packet_within_update_rate_window_is_dropped(self, monkeypatch):
        monkeypatch.setattr(main.config, "UPDATE_RATE", 100.0)  # huge window, nothing should get through twice
        raw = json.dumps({"d": {"TEST-1": {"heading": 1, "groundSpeed": 1, "altitude": 1, "isOnGround": False}}})
        main.handle_packet(raw)
        first_snapshot = dict(main.ACdata["TEST-1"])
        raw2 = json.dumps({"d": {"TEST-1": {"heading": 999, "groundSpeed": 999, "altitude": 999, "isOnGround": False}}})
        main.handle_packet(raw2)
        # Second packet arrived inside the rate-limit window and must be dropped untouched
        assert main.ACdata["TEST-1"] == first_snapshot

    def test_invalid_json_raises(self):
        with pytest.raises(json.JSONDecodeError):
            main.handle_packet("{not valid json")
