"""Tool check_holiday.

Mục đích: tìm ra các ngày lễ, kỳ nghỉ, cuối tuần dài hoặc giai đoạn cao điểm
gần ngày được hỏi. Kết quả dùng để cảnh báo đông người, giá tăng, cần đặt sớm,
hoặc nên đổi giờ/tuyến/địa điểm.
"""

from __future__ import annotations


def check_holiday(user_request: str) -> dict:
    return {
        "tool_name": "check_holiday",
        "status": "simulated",
        "summary": (
            "Demo: không phát hiện ngày lễ lớn chắc chắn, nhưng nếu đi cuối tuần "
            "ở Hà Nội vẫn nên giả định lượng khách tăng tại khu hồ, phố cổ, bảo tàng."
        ),
        "findings": [
            "Cuối tuần thường đông hơn ngày thường tại điểm trung tâm.",
            "Nên đi sớm trước 9:00 hoặc chọn khung sau 15:00 cho điểm ngoài trời.",
            "Nếu người dùng cung cấp ngày cụ thể, tool live sẽ kiểm tra lịch nghỉ/lễ chính xác.",
        ],
        "input_hint": user_request,
        "verified": "simulated_for_demo",
    }
