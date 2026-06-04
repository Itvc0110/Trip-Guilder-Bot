"""Tool calendar_export.

Mục đích: chuyển lịch trình đã được người dùng duyệt thành dữ liệu calendar
hoặc file ICS. Tool này chỉ nên chạy sau khi kế hoạch đủ rõ về ngày, giờ, địa
điểm và người dùng đã chấp nhận bản nháp.
"""

from __future__ import annotations


def calendar_export(user_request: str) -> dict:
    return {
        "tool_name": "calendar_export",
        "status": "placeholder",
        "summary": (
            "Xuất calendar chưa triển khai thật. Tool này sẽ chuyển lịch trình "
            "đã duyệt thành dữ liệu calendar/ICS khi ngày, giờ và địa điểm đủ rõ."
        ),
        "input_hint": user_request,
        "verified": False,
    }
