from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Any

INTEGRATION_ROOT = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "anycubic_ha_integration"
)
sys.path.insert(0, str(INTEGRATION_ROOT))

from anycubic_cloud_api.api.functions import AnycubicAPIFunctions  # noqa: E402
from anycubic_cloud_api.const.api_endpoints import API_ENDPOINT  # noqa: E402


@dataclass
class StubPrinter:
    id: int


class RecordingAPI(AnycubicAPIFunctions):
    def __init__(self) -> None:
        self.calls: list[tuple[Any, dict[str, Any]]] = []

    async def _fetch_api_resp(self, endpoint: Any, params: dict[str, Any] | None = None, **_: Any) -> dict[str, Any]:
        self.calls.append((endpoint, params or {}))
        return {"code": 1, "msg": "", "data": {"msgid": "close-msg"}}


class CameraCloseTests(unittest.IsolatedAsyncioTestCase):
    async def test_close_camera_sends_camera_close_order_for_printer(self) -> None:
        api = RecordingAPI()

        result = await api.close_camera(StubPrinter(id=42))

        self.assertEqual(result, "close-msg")
        self.assertEqual(api.calls, [(API_ENDPOINT.send_order, {"order_id": 1002, "printer_id": 42})])

    async def test_close_camera_without_printer_sends_nothing(self) -> None:
        api = RecordingAPI()

        self.assertIsNone(await api.close_camera(None))  # type: ignore[arg-type]
        self.assertEqual(api.calls, [])


if __name__ == "__main__":
    unittest.main()
