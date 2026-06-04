"""Tool weather_safety.

Mục đích: kiểm tra thời tiết, mưa, nắng nóng, bão, chất lượng không khí và rủi
ro an toàn theo ngày/địa điểm. Kết quả nên kết hợp với search_attractions để đề
xuất điểm trong nhà hoặc đổi giờ đi.
"""

from __future__ import annotations


def weather_safety(user_request: str) -> dict:
    return {
        "tool_name": "weather_safety",
        "status": "simulated",
        "summary": (
            "Demo: thời tiết được giả lập ở mức cần có phương án dự phòng; nên "
            "kết hợp search_attractions để chọn điểm trong nhà nếu mưa/nắng gắt."
        ),
        "findings": [
            "Nên có ít nhất một điểm trong nhà làm backup.",
            "Tránh hoạt động ngoài trời kéo dài giữa trưa.",
            "Nếu có trẻ em/người lớn tuổi, thêm điểm nghỉ có điều hòa hoặc cafe gần tuyến.",
        ],
        "input_hint": user_request,
        "verified": "simulated_for_demo",
    }
