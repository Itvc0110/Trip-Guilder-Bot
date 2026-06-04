"""Tool check_events.

Mục đích: tìm các sự kiện lớn gần điểm đến và ngày đi, ví dụ concert, lễ hội,
giải thể thao, hội chợ hoặc sự kiện địa phương. Kết quả cần được kết hợp với
route_advice để cảnh báo khu vực đông, đường có thể tắc, nên đi sớm hoặc đổi
tuyến.
"""

from __future__ import annotations


def check_events(user_request: str) -> dict:
    return {
        "tool_name": "check_events",
        "status": "placeholder",
        "summary": (
            "Tìm kiếm sự kiện chưa live. Tool này sẽ tìm sự kiện gần điểm "
            "đến/ngày đi và kết hợp với route_advice để cảnh báo đông người, "
            "tắc đường hoặc nên đổi tuyến."
        ),
        "input_hint": user_request,
        "verified": False,
    }
