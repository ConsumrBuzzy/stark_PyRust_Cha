import asyncio

from src.ops.reporting_ops import send_pulse


class DummyTelegram:
    def __init__(self):
        self.sent = []

    async def send_alert(self, pulse_type: str, message: str):
        self.sent.append((pulse_type, message))
        return True


class DummyReporting:
    def __init__(self, enabled: bool = True):
        self._enabled = enabled
        self.telegram = DummyTelegram()

    def is_enabled(self):
        return self._enabled


def test_send_pulse_enabled():
    reporting = DummyReporting(enabled=True)
    ok = asyncio.run(send_pulse("TEST", "msg", reporting=reporting))
    assert ok is True
    assert reporting.telegram.sent == [("TEST", "msg")]


def test_send_pulse_disabled():
    reporting = DummyReporting(enabled=False)
    ok = asyncio.run(send_pulse("TEST", "msg", reporting=reporting))
    assert ok is False
    assert reporting.telegram.sent == []
