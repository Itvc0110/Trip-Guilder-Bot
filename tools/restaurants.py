"""Tool search_restaurants.

Mục đích: tìm nhà hàng/quán ăn phù hợp với vị trí, ngân sách, khẩu vị, ăn kiêng
và thời điểm trong lịch trình. Kết quả nên kết hợp với route_advice để chọn quán
gần tuyến đi, giảm vòng vèo và tránh giờ cao điểm.
"""

from __future__ import annotations


def search_restaurants(user_request: str) -> dict:
    return {
        "tool_name": "search_restaurants",
        "status": "simulated",
        "summary": (
            "Demo: đã tìm nhóm quán phù hợp theo khẩu vị/ngân sách và ưu tiên "
            "quán thuận tuyến thay vì chỉ chọn rating cao."
        ),
        "findings": [
            "Nếu food tour: ưu tiên 2-3 điểm ăn chính, không nhồi quá nhiều món.",
            "Nếu ăn chay/ăn kiêng: cần xác nhận menu trước khi đi.",
            "Kết hợp route_advice để chọn quán gần điểm tham quan kế tiếp.",
        ],
        "input_hint": user_request,
        "verified": "simulated_for_demo",
    }
