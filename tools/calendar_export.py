"""Tool calendar_export.

Mục đích: chuyển lịch trình đã được người dùng duyệt thành dữ liệu calendar
hoặc file ICS. Tool này chỉ nên chạy sau khi kế hoạch đủ rõ về ngày, giờ, địa
điểm và người dùng đã chấp nhận bản nháp.
"""

from __future__ import annotations


def calendar_export(user_request: str) -> dict:
    return {
        "tool_name": "calendar_export",
        "status": "simulated",
        "summary": (
            "Demo: lịch có thể xuất calendar sau khi người dùng xác nhận ngày, "
            "giờ và danh sách điểm cuối cùng."
        ),
        "findings": [
            "Chưa nên export nếu còn thiếu ngày/giờ cụ thể.",
            "Sau khi người dùng duyệt plan, chuyển từng stop thành event.",
            "Mỗi event cần title, start, end, location và note cảnh báo.",
        ],
        "input_hint": user_request,
        "verified": "simulated_for_demo",
    }
