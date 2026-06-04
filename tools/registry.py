"""Registry cho tool chain gợi ý địa điểm theo review.

Active flow hiện tại:
1. `search_places`: tìm địa điểm từ một query kiểu Google Maps search bar.
2. `review_search`: đọc review cho từng địa điểm, ưu tiên `data_id`.
3. `filter_reviews`: lọc/xếp hạng địa điểm theo nhu cầu user và review.

Các tool cũ vẫn có thể tồn tại trong thư mục `tools/`, nhưng không còn nằm
trong luồng chính của scope mới.
"""

from __future__ import annotations

<<<<<<< HEAD
from database import save_search_result
from tools.place_search import search_attractions


TOOL_REGISTRY = {}

# Nhập các tools khác (do người khác implement)
try:
    from tools.calendar_export import calendar_export
    TOOL_REGISTRY["calendar_export"] = calendar_export
except ImportError:
    pass

try:
    from tools.events import check_events
    TOOL_REGISTRY["check_events"] = check_events
except ImportError:
    pass

try:
    from tools.holidays import check_holiday
    TOOL_REGISTRY["check_holiday"] = check_holiday
except ImportError:
    pass

try:
    from tools.restaurants import search_restaurants
    TOOL_REGISTRY["search_restaurants"] = search_restaurants
except ImportError:
    pass

try:
    from tools.routes import route_advice
    TOOL_REGISTRY["route_advice"] = route_advice
except ImportError:
    pass

try:
    from tools.weather import weather_safety
    TOOL_REGISTRY["weather_safety"] = weather_safety
except ImportError:
    pass

# Search attractions - có xử lý lưu ảnh vào database
TOOL_REGISTRY["search_attractions"] = search_attractions


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

        result = tool(user_request)
        findings.append(result)

        # Lưu search results vào database với ảnh
        if tool_name in ("search_attractions", "search_restaurants") and result.get("status") == "success":
            _save_places_to_db(result.get("places", []))

=======
from typing import Any

from tools.filter_review import filter_reviews
from tools.place_search import search_places
from tools.review_search import review_search


ACTIVE_TOOL_NAMES = ["search_places", "review_search", "filter_reviews"]


TOOL_REGISTRY = {
    "search_places": search_places,
    "review_search": review_search,
    "filter_reviews": filter_reviews,
}


def run_placeholder_tools(route: dict[str, Any], user_request: str) -> list[dict[str, Any]]:
    """Run the active place recommendation pipeline.

    The name is kept for backward compatibility with `agent.py`.
    """
    if route.get("decision") != "plan":
        return []

    findings: list[dict[str, Any]] = []
    place_result = search_places(user_request)
    findings.append(place_result)

    places = place_result.get("places") or []
    places_with_reviews = []
    if not places:
        findings.append(
            {
                "tool_name": "review_search",
                "status": "unavailable",
                "summary": "Chưa có địa điểm từ search_places nên chưa thể đọc review.",
                "place": None,
                "reviews": [],
                "verified": False,
            }
        )

    for place in places:
        review_result = review_search(place)
        findings.append(review_result)
        places_with_reviews.append(
            {
                "place": place,
                "status": review_result.get("status"),
                "reviews": review_result.get("reviews") or [],
                "review_summary": review_result.get("summary"),
            }
        )

    filter_result = filter_reviews(user_request, places_with_reviews)
    findings.append(filter_result)
>>>>>>> 286cca25caec194fe697f6312627054eb3f29d0e
    return findings


def _save_places_to_db(places: list[dict]) -> None:
    """Lưu danh sách địa điểm từ search vào database với ảnh."""
    for place in places:
        try:
            # Chuẩn bị dữ liệu cho database
            place_data = {
                "title": place.get("title"),
                "address": place.get("address"),
                "latitude": _extract_lat(place.get("gps")),
                "longitude": _extract_lng(place.get("gps")),
                "rating": place.get("rating", 0),
                "reviews": place.get("reviews", 0),
                "price": place.get("price", ""),
                "type": place.get("type", ""),
                "open_state": place.get("open_state", ""),
                "images": place.get("images", []),
                "data_id": place.get("data_id", ""),
            }
            save_search_result(place_data)
        except Exception:
            # Log error nhưng không break flow
            pass


def _extract_lat(gps: dict | None) -> float:
    """Extract latitude từ GPS dict."""
    if not gps or not isinstance(gps, dict):
        return 0.0
    return float(gps.get("latitude", 0) or 0)


def _extract_lng(gps: dict | None) -> float:
    """Extract longitude từ GPS dict."""
    if not gps or not isinstance(gps, dict):
        return 0.0
    return float(gps.get("longitude", 0) or 0)
