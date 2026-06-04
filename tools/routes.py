"""Tool route_advice.

Mục đích: phân tích thứ tự đi, khoảng cách, phương tiện, thời gian di chuyển,
khu vực có thể đông/tắc và điểm cần tránh. Tool này thường phải kết hợp với
check_events, check_holiday, search_restaurants và search_attractions để đưa ra
lời khuyên tuyến đường thực tế hơn.
"""

from __future__ import annotations


def route_advice(user_request: str) -> dict:
    return {
        "tool_name": "route_advice",
        "status": "placeholder",
        "summary": (
            "Gợi ý tuyến đường hiện chỉ là placeholder. Tool này sẽ phân tích "
            "thứ tự đi, khoảng cách, phương tiện, khu đông/tắc và kết hợp "
            "event/holiday/restaurant/attraction."
        ),
        "input_hint": user_request,
        "verified": False,
    }
