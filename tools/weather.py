"""Tool weather_safety.

Mục đích: kiểm tra thời tiết, mưa, nắng nóng, bão, chất lượng không khí và rủi
ro an toàn theo ngày/địa điểm. Kết quả nên kết hợp với search_attractions để đề
xuất điểm trong nhà hoặc đổi giờ đi.
"""

from __future__ import annotations


def weather_safety(user_request: str) -> dict:
    return {
        "tool_name": "weather_safety",
        "status": "placeholder",
        "summary": (
            "Dữ liệu thời tiết và an toàn chưa live. Tool này sẽ kiểm tra mưa, "
            "nắng nóng, bão, không khí xấu và kết hợp search_attractions để "
            "gợi ý phương án trong nhà."
        ),
        "input_hint": user_request,
        "verified": False,
    }
