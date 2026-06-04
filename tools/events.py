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
        "status": "simulated",
        "summary": (
            "Demo: giả lập có khả năng có hoạt động cuối tuần quanh khu trung tâm "
            "và hồ, nên kết hợp route_advice để tránh tuyến quá đông."
        ),
        "findings": [
            "Khu Hoàn Kiếm/phố cổ có thể đông vào chiều tối cuối tuần.",
            "Nếu có sự kiện quanh hồ hoặc phố đi bộ, nên tránh đưa xe vào lõi trung tâm.",
            "Ưu tiên taxi/đi bộ đoạn ngắn hoặc đổi sang điểm gần hơn nếu có trẻ em.",
        ],
        "input_hint": user_request,
        "verified": "simulated_for_demo",
    }
