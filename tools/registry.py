"""Registry cho toàn bộ tool của Trip-Guilder-Bot.

Mục đích: gom các tool có thể dùng, chạy đúng tool theo quyết định của router,
và trả kết quả có cấu trúc cho model. Registry không tự suy luận nội dung chuyến
đi; nó chỉ điều phối tool và giữ trạng thái placeholder/unavailable rõ ràng.
"""

from __future__ import annotations

from tools.calendar_export import calendar_export
from tools.events import check_events
from tools.holidays import check_holiday
from tools.place_search import search_attractions
from tools.restaurants import search_restaurants
from tools.routes import route_advice
from tools.weather import weather_safety


TOOL_REGISTRY = {
    "check_holiday": check_holiday,
    "check_events": check_events,
    "search_restaurants": search_restaurants,
    "search_attractions": search_attractions,
    "route_advice": route_advice,
    "weather_safety": weather_safety,
    "calendar_export": calendar_export,
}


def run_placeholder_tools(route: dict, user_request: str) -> list[dict]:
    findings = []
    for tool_name in route.get("tools_to_use", []):
        tool = TOOL_REGISTRY.get(tool_name)
        if not tool:
            findings.append(
                {
                    "tool_name": tool_name,
                    "status": "unavailable",
                    "summary": "Tool chưa được đăng ký.",
                    "verified": False,
                }
            )
            continue
        findings.append(tool(user_request))
    return findings
