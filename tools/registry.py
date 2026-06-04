"""Registry cho tool chain gợi ý địa điểm theo review.

Active flow hiện tại:
1. `search_places`: tìm địa điểm từ một query kiểu Google Maps search bar.
2. `search_reviews`: đọc review cho từng địa điểm, ưu tiên `data_id`.
3. `filter_reviews`: lọc/xếp hạng địa điểm theo nhu cầu user và review.

Các tool cũ vẫn có thể tồn tại trong thư mục `tools/`, nhưng không còn nằm
trong luồng chính của scope mới.
"""

from __future__ import annotations

from typing import Any

from tools.filter_review import filter_reviews
from tools.place_search import search_places
from tools.review_search import search_reviews


ACTIVE_TOOL_NAMES = ["search_places", "search_reviews", "filter_reviews"]


TOOL_REGISTRY = {
    "search_places": search_places,
    "search_reviews": search_reviews,
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
                "tool_name": "search_reviews",
                "status": "unavailable",
                "summary": "Chưa có địa điểm từ search_places nên chưa thể đọc review.",
                "place": None,
                "reviews": [],
                "verified": False,
            }
        )

    for place in places:
        review_result = search_reviews(place)
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
    return findings
