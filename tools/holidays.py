"""Tool check_holiday.

Mục đích: tìm ra các ngày lễ, kỳ nghỉ, cuối tuần dài hoặc giai đoạn cao điểm
gần ngày được hỏi. Kết quả dùng để cảnh báo đông người, giá tăng, cần đặt sớm,
hoặc nên đổi giờ/tuyến/địa điểm.
"""

from __future__ import annotations


def check_holiday(user_request: str) -> dict:
    return {
        "tool_name": "check_holiday",
        "status": "placeholder",
        "summary": (
            "Dữ liệu ngày lễ chưa live. Tool này sẽ tìm ngày lễ/kỳ nghỉ gần "
            "ngày được hỏi để cảnh báo đông người, giá tăng và nhu cầu đặt trước."
        ),
        "input_hint": user_request,
        "verified": False,
    }
