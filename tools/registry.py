"""Registry cho tool chain gợi ý địa điểm theo review.

Active flow hiện tại:
1. `search_places`: tìm địa điểm từ một query kiểu Google Maps search bar.
2. `review_search`: đọc review cho từng địa điểm, ưu tiên `data_id`.
3. `filter_reviews`: lọc/xếp hạng địa điểm theo nhu cầu user và review.

Các tool cũ vẫn có thể tồn tại trong thư mục `tools/`, nhưng không còn nằm
trong luồng chính của scope mới.
"""

from __future__ import annotations

from database import save_search_result
from tools.place_search import search_attractions


TOOL_REGISTRY = {}

# Nhập các tools khác (do người khác implement)

try:
    from tools.routes import route_advice
    TOOL_REGISTRY["route_advice"] = route_advice
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
