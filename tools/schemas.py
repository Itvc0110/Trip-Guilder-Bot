"""Schema mô tả mục đích và tham số của các tool.

Các schema này giúp prompt/router hiểu tool nào dùng để làm gì. Khi phát triển
tool live, có thể chuyển các schema này thành OpenRouter/OpenAI-compatible tool
definitions.
"""

from __future__ import annotations


TOOL_SCHEMAS = [
    {
        "name": "check_holiday",
        "description": "Tìm ngày lễ, kỳ nghỉ hoặc giai đoạn cao điểm gần ngày đi.",
        "parameters": ["destination", "travel_dates"],
    },
    {
        "name": "check_events",
        "description": "Tìm sự kiện quan trọng gần điểm đến và ngày đi.",
        "parameters": ["destination", "travel_dates"],
    },
    {
        "name": "search_restaurants",
        "description": "Tìm nhà hàng theo vị trí, ngân sách và sở thích ăn uống.",
        "parameters": ["destination", "food_preferences", "budget"],
    },
    {
        "name": "search_attractions",
        "description": "Tìm điểm tham quan theo mục đích, nhóm người đi, tiếp cận và thời gian.",
        "parameters": ["destination", "purpose", "constraints"],
    },
    {
        "name": "route_advice",
        "description": "Gợi ý thứ tự tuyến, phương tiện, khoảng cách, độ đông và lưu ý giao thông.",
        "parameters": ["places", "transport", "time_window"],
    },
    {
        "name": "weather_safety",
        "description": "Kiểm tra thời tiết, chất lượng không khí và rủi ro an toàn.",
        "parameters": ["destination", "travel_dates"],
    },
    {
        "name": "calendar_export",
        "description": "Chuẩn bị lịch trình để xuất calendar/ICS.",
        "parameters": ["itinerary"],
    },
]
