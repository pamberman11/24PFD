import importlib
import os

import config


class TestConfigDefaults:
    def test_default_ws_uri(self):
        assert config.WS_URI == "wss://ws.awdevhardware.org"

    def test_default_relay_port_is_int(self):
        assert isinstance(config.RELAY_PORT, int)
        assert config.RELAY_PORT == 8765

    def test_default_update_rate_is_float(self):
        assert isinstance(config.UPDATE_RATE, float)


class TestConfigEnvOverrides:
    def test_env_var_overrides_relay_port(self, monkeypatch):
        monkeypatch.setenv("PFD_RELAY_PORT", "9999")
        reloaded = importlib.reload(config)
        try:
            assert reloaded.RELAY_PORT == 9999
        finally:
            monkeypatch.delenv("PFD_RELAY_PORT", raising=False)
            importlib.reload(config)  # restore defaults for subsequent tests

    def test_env_var_overrides_ws_uri(self, monkeypatch):
        monkeypatch.setenv("PFD_UPSTREAM_WS_URI", "wss://example.test/ws")
        reloaded = importlib.reload(config)
        try:
            assert reloaded.WS_URI == "wss://example.test/ws"
        finally:
            monkeypatch.delenv("PFD_UPSTREAM_WS_URI", raising=False)
            importlib.reload(config)
