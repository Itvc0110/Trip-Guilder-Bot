"""Tool search_reviews — Lấy review thô từ Google Maps.

Nhiệm vụ chính:
- Lấy tối đa 10 review thô (5 review đánh giá cao nhất + 5 review đánh giá thấp nhất).
- Trả về đầy đủ thông tin: user (tên người comment), rating (score), date (thời gian), snippet (nội dung comment).
- Không tóm tắt, không lọc, không bịa dữ liệu — chỉ trả review nguyên bản.

Vị trí trong pipeline: 
    search_places → search_reviews → filter_reviews
"""

from __future__ import annotations

import os
from typing import Any

import requests


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SERPAPI_URL = "https://serpapi.com/search"

# Số review tối đa mỗi chiều
DEFAULT_MAX_HIGH = 5
DEFAULT_MAX_LOW = 5


TOOL_DEFINITION = {
    "name": "search_reviews",
    "description": (
        "Lấy review thực tế của một địa điểm Google Maps: "
        f"{DEFAULT_MAX_HIGH} review đánh giá cao nhất và {DEFAULT_MAX_LOW} review đánh giá thấp nhất. "
        "Trả về review thô (user, rating, date, snippet) để filter_reviews xử lý tiếp."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "place": {
                "type": "object",
                "description": "Một phần tử trong danh sách 'places' từ kết quả search_places.",
            },
            "max_high": {
                "type": "integer",
                "description": f"Số review cao nhất muốn lấy. Mặc định {DEFAULT_MAX_HIGH}.",
            },
            "max_low": {
                "type": "integer",
                "description": f"Số review thấp nhất muốn lấy. Mặc định {DEFAULT_MAX_LOW}.",
            },
        },
        "required": ["place"],
    },
}


def search_reviews(
    place: dict[str, Any],
    max_high: int = DEFAULT_MAX_HIGH,
    max_low: int = DEFAULT_MAX_LOW,
) -> dict[str, Any]:
    """Đọc review thực tế cho một địa điểm theo data_id từ SerpAPI."""
    if not isinstance(place, dict):
        return _error_result("place phải là dict từ kết quả search_places.")

    data_id = str(place.get("data_id") or "").strip()
    place_name = str(place.get("title") or "").strip()
    place_addr = str(place.get("address") or "").strip()
    display_name = place_name or data_id or "địa điểm không rõ tên"

    if not data_id:
        return _error_result(
            f"data_id rỗng cho địa điểm '{display_name}'.",
            place_name=place_name,
            place_addr=place_addr,
        )

    # Kiểm tra API key
    api_key = os.getenv("SERPAPI_API_KEY", "").strip()
    if not api_key or api_key in ("optional_for_live_place_and_review_tools", "optional_for_future_tools"):
        return {
            "tool_name": "search_reviews",
            "status": "unavailable",
            "summary": f"Chưa có SERPAPI_API_KEY — chưa thể lấy review thật cho '{display_name}'.",
            "place_name": place_name,
            "place_addr": place_addr,
            "data_id": data_id,
            "reviews": [],
            "high_count": 0,
            "low_count": 0,
            "verified": False,
        }

    # Gọi 2 lần SerpAPI
    high_reviews, fetched_name_high = _fetch_reviews(
        data_id=data_id, api_key=api_key, sort_by="ratingHigh", max_count=max_high
    )
    low_reviews, fetched_name_low = _fetch_reviews(
        data_id=data_id, api_key=api_key, sort_by="ratingLow", max_count=max_low
    )

    # Ưu tiên tên từ API
    if not place_name:
        place_name = fetched_name_high or fetched_name_low or data_id

    # Gắn nhãn
    for r in high_reviews:
        r["_sort_by"] = "ratingHigh"
    for r in low_reviews:
        r["_sort_by"] = "ratingLow"

    all_reviews = high_reviews + low_reviews
    high_count = len(high_reviews)
    low_count = len(low_reviews)
    total = high_count + low_count

    # Xác định status
    if total == 0:
        status = "partial"
        summary = f"Không lấy được review nào cho '{place_name}'."
    elif high_count < max_high or low_count < max_low:
        status = "partial"
        summary = f"Lấy được {total} review cho '{place_name}' ({high_count} cao + {low_count} thấp)."
    else:
        status = "success"
        summary = f"Lấy được {total} review cho '{place_name}' (5 cao nhất + 5 thấp nhất)."

    return {
        "tool_name": "search_reviews",
        "status": status,
        "summary": summary,
        "place_name": place_name,
        "place_addr": place_addr,
        "data_id": data_id,
        "reviews": all_reviews,
        "high_count": high_count,
        "low_count": low_count,
        "verified": total > 0,
    }


# ---------------------------------------------------------------------------
# Internal Functions
# ---------------------------------------------------------------------------
def _fetch_reviews(
    data_id: str, api_key: str, sort_by: str, max_count: int
) -> tuple[list[dict[str, Any]], str]:
    """Gọi SerpAPI lấy review theo sort."""
    if max_count <= 0:
        return [], ""

    try:
        response = requests.get(
            SERPAPI_URL,
            params={
                "engine": "google_maps_reviews",
                "data_id": data_id,
                "hl": "vi",
                "sort_by": sort_by,
                "api_key": api_key,
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except Exception:
        return [], ""

    if data.get("error"):
        return [], ""

    fetched_name = ""
    place_info = data.get("place_info")
    if isinstance(place_info, dict):
        fetched_name = str(place_info.get("title") or "").strip()

    raw_reviews = data.get("reviews") or []
    if not isinstance(raw_reviews, list):
        return [], fetched_name

    normalized = [_normalize_review(r) for r in raw_reviews[:max_count]]
    return normalized, fetched_name


def _normalize_review(review: dict[str, Any]) -> dict[str, Any]:
    """Chuẩn hóa review thô từ SerpAPI."""
    user_field = review.get("user")
    if isinstance(user_field, dict):
        username = user_field.get("name") or user_field.get("link") or None
    elif isinstance(user_field, str):
        username = user_field or None
    else:
        username = None

    return {
        "user": username,
        "rating": review.get("rating"),
        "date": review.get("date") or review.get("iso_date") or None,
        "snippet": review.get("snippet") or review.get("text") or None,
        "likes": review.get("likes"),
        "source": review.get("source"),
    }


def _error_result(
    message: str,
    place_name: str = "",
    place_addr: str = "",
    data_id: str | None = None,
) -> dict[str, Any]:
    return {
        "tool_name": "search_reviews",
        "status": "error",
        "summary": message,
        "place_name": place_name,
        "place_addr": place_addr,
        "data_id": data_id,
        "reviews": [],
        "high_count": 0,
        "low_count": 0,
        "verified": False,
    }


# ---------------------------------------------------------------------------
# Backward Compatibility
# ---------------------------------------------------------------------------
def get_place_reviews(
    data_id: str, max_best: int = 5, max_worst: int = 5
) -> dict[str, Any]:
    """Alias cho test cũ."""
    return search_reviews(
        place={"data_id": data_id}, max_high=max_best, max_low=max_worst
    )


def search_reviews_for_places(
    places: list[dict[str, Any]],
    max_high: int = DEFAULT_MAX_HIGH,
    max_low: int = DEFAULT_MAX_LOW,
) -> list[dict[str, Any]]:
    """Lấy review cho nhiều địa điểm."""
    return [
        search_reviews(place, max_high=max_high, max_low=max_low)
        for place in places
        if isinstance(place, dict) and place.get("data_id")
    ]
