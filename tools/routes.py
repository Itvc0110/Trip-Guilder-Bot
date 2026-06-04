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
        "status": "simulated",
        "summary": (
            "Demo: route_advice đã nhóm điểm theo logic giảm vòng vèo, tránh khu "
            "đông khi có event/holiday và chừa buffer di chuyển."
        ),
        "findings": [
            "Nhóm điểm theo cụm: Cầu Giấy/Ba Đình trước, Tây Hồ hoặc Hoàn Kiếm sau.",
            "Chừa 25-40 phút giữa hai điểm khác quận.",
            "Nếu check_events cảnh báo đông, tránh lõi Hoàn Kiếm vào chiều tối.",
            "Nếu đi với trẻ em, không nên quá 3-4 điểm chính/ngày.",
        ],
        "input_hint": user_request,
        "verified": "simulated_for_demo",
    }
