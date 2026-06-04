"""Tool search_attractions.

Mục đích: tìm điểm tham quan phù hợp với mục đích chuyến đi, nhóm người đi,
độ tuổi trẻ em, nhu cầu tiếp cận, thời lượng và ngân sách. Kết quả nên kết hợp
với weather_safety và route_advice để chọn điểm trong nhà/ngoài trời và thứ tự
đi hợp lý.
"""

from __future__ import annotations


def search_attractions(user_request: str) -> dict:
    return {
        "tool_name": "search_attractions",
        "status": "simulated",
        "summary": (
            "Demo: đã tìm nhóm điểm tham quan theo sở thích, độ tuổi, thời lượng "
            "và khả năng kết hợp với weather_safety/route_advice."
        ),
        "findings": [
            "Gia đình có trẻ em: ưu tiên bảo tàng, công viên, sở thú, hồ/cafe nghỉ.",
            "Sightseeing/văn hóa: ưu tiên Văn Miếu, Bảo tàng Dân tộc học, Hoàn Kiếm.",
            "Nếu thời tiết xấu: đẩy điểm trong nhà lên trước.",
            "Nếu route xa nhau: tách must-have và optional.",
        ],
        "input_hint": user_request,
        "verified": "simulated_for_demo",
    }
