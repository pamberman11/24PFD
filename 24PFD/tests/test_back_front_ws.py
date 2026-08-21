import back_front_ws


class TestUpdateAcdataws:
    def test_updates_module_level_state(self):
        back_front_ws.update_acdataws({"TEST-1": {"roll": 5}})
        assert back_front_ws.acdataws == {"TEST-1": {"roll": 5}}

    def test_overwrites_previous_state_entirely(self):
        back_front_ws.update_acdataws({"TEST-1": {"roll": 5}})
        back_front_ws.update_acdataws({"TEST-2": {"roll": 9}})
        assert "TEST-1" not in back_front_ws.acdataws
        assert back_front_ws.acdataws == {"TEST-2": {"roll": 9}}

    def test_empty_dict_clears_state(self):
        back_front_ws.update_acdataws({"TEST-1": {"roll": 5}})
        back_front_ws.update_acdataws({})
        assert back_front_ws.acdataws == {}
