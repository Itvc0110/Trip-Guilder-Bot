"""Tool search_restaurants.

Mục đích: tìm nhà hàng/quán ăn phù hợp với vị trí, ngân sách, khẩu vị, ăn kiêng
và thời điểm trong lịch trình. Kết quả nên kết hợp với route_advice để chọn quán
gần tuyến đi, giảm vòng vèo và tránh giờ cao điểm.
"""

from __future__ import annotations


def search_restaurants(user_request: str) -> dict:
    return {
        "tool_name": "search_restaurants",
        "status": "placeholder",
        "summary": (
            "Tìm nhà hàng chưa live. Tool này sẽ tìm quán theo vị trí, ngân "
            "sách, khẩu vị/ăn kiêng và kết hợp route_advice để chọn điểm ăn "
            "thuận tuyến."
        ),
        "input_hint": user_request,
        "verified": False,
    }
