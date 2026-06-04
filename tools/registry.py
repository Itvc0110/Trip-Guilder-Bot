"""Registry cho active tools của DiChoiBot.

Luồng chính hiện tại:
1. `search_places(query)`: tìm địa điểm bằng một query kiểu Google Maps.
2. `review_search(place)`: đọc review cho từng địa điểm, ưu tiên `data_id`.
3. `filter_reviews(user_request, places_with_reviews)`: xếp hạng địa điểm theo
   nhu cầu người dùng và review.

Tên `run_placeholder_tools` được giữ để tương thích với `agent.py`, nhưng hàm
này đang chạy pipeline thật/available theo tool hiện có.
"""

from __future__ import annotations

from typing import Any, Callable

from tools.filter_review import TOOL_DEFINITION as FILTER_REVIEWS_DEFINITION
from tools.filter_review import filter_reviews
from tools.place_search import TOOL_DEFINITION as SEARCH_PLACES_DEFINITION
from tools.place_search import search_attractions, search_places
from tools.review_search import TOOL_DEFINITION as REVIEW_SEARCH_DEFINITION
from tools.review_search import review_search, search_reviews


ToolFn = Callable[..., dict[str, Any]]


ACTIVE_PIPELINE = ["search_places", "review_search", "filter_reviews"]


TOOL_REGISTRY: dict[str, ToolFn] = {
    "search_places": search_places,
    "review_search": review_search,
    "search_reviews": search_reviews,
    "filter_reviews": filter_reviews,
    # Backward-compatible alias. The active router should prefer search_places.
    "search_attractions": search_attractions,
}


TOOL_DEFINITIONS = {
    "search_places": SEARCH_PLACES_DEFINITION,
    "review_search": REVIEW_SEARCH_DEFINITION,
    "search_reviews": REVIEW_SEARCH_DEFINITION,
    "filter_reviews": FILTER_REVIEWS_DEFINITION,
}


def run_placeholder_tools(route: dict[str, Any], user_request: str) -> list[dict[str, Any]]:
    """Run DiChoiBot's place/review/filter pipeline.

    If router returns `plan`, run the canonical pipeline regardless of aliases in
    `tools_to_use`. If router does not return `plan`, return no findings.
    """
    if route.get("decision") != "plan":
        return []

    findings: list[dict[str, Any]] = []

    place_result = search_places(user_request)
    findings.append(place_result)

    places = place_result.get("places") or []
    places_with_reviews: list[dict[str, Any]] = []

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
    else:
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

    findings.append(filter_reviews(user_request, places_with_reviews))
    return findings


def get_tool(tool_name: str) -> ToolFn | None:
    """Return a registered tool by name."""
    return TOOL_REGISTRY.get(tool_name)
