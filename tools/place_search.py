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
        "status": "placeholder",
        "summary": (
            "Tìm điểm tham quan chưa live. Tool này sẽ tìm điểm theo sở thích, "
            "độ tuổi, tiếp cận, thời lượng và kết hợp weather_safety/route_advice "
            "để chọn lịch phù hợp."
        ),
        "input_hint": user_request,
        "verified": False,
    }
