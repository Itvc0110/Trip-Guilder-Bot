"""Tool search_reviews - lay review tho tu Google Maps qua SerpAPI.

Pipeline:
    search_places -> search_reviews -> filter_reviews

Tool nay chi lay review tho, khong tom tat, khong loc, khong bia du lieu.
Mac dinh lay toi da 10 review: 5 review rating cao nhat va 5 review rating
thap nhat.
"""

from __future__ import annotations

import os
from typing import Any

import requests


SERPAPI_URL = "https://serpapi.com/search"
DEFAULT_MAX_HIGH = 5
DEFAULT_MAX_LOW = 5


TOOL_DEFINITION = {
    "name": "search_reviews",
    "description": (
        "Lay review thuc te cua mot dia diem Google Maps: "
        f"{DEFAULT_MAX_HIGH} review danh gia cao nhat va {DEFAULT_MAX_LOW} review danh gia thap nhat. "
        "Tra ve review tho de filter_reviews xu ly tiep."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "place": {
                "type": "object",
                "description": "Mot phan tu trong danh sach places tu search_places.",
            },
            "max_high": {
                "type": "integer",
                "description": f"So review cao nhat muon lay. Mac dinh {DEFAULT_MAX_HIGH}.",
            },
            "max_low": {
                "type": "integer",
                "description": f"So review thap nhat muon lay. Mac dinh {DEFAULT_MAX_LOW}.",
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
    """Doc review thuc te cho mot dia diem theo data_id tu SerpAPI."""
    if not isinstance(place, dict):
        return _error_result("place phai la dict tu ket qua search_places.")

    data_id = str(place.get("data_id") or "").strip()
    place_name = str(place.get("title") or place.get("place_name") or "").strip()
    place_addr = str(place.get("address") or place.get("place_addr") or "").strip()
    display_name = place_name or data_id or "dia diem khong ro ten"

    if not data_id:
        return _error_result(
            f"data_id rong cho dia diem '{display_name}'.",
            place_name=place_name,
            place_addr=place_addr,
        )

    api_key = os.getenv("SERPAPI_API_KEY", "").strip()
    if not api_key or api_key in {"optional_for_live_place_and_review_tools", "optional_for_future_tools"}:
        return {
            "tool_name": "search_reviews",
            "status": "unavailable",
            "summary": f"Chua co SERPAPI_API_KEY nen chua the lay review that cho '{display_name}'.",
            "place_name": place_name,
            "place_addr": place_addr,
            "data_id": data_id,
            "reviews": [],
            "high_count": 0,
            "low_count": 0,
            "verified": False,
        }

    high_reviews, fetched_name_high = _fetch_reviews(
        data_id=data_id,
        api_key=api_key,
        sort_by="ratingHigh",
        max_count=max_high,
    )
    low_reviews, fetched_name_low = _fetch_reviews(
        data_id=data_id,
        api_key=api_key,
        sort_by="ratingLow",
        max_count=max_low,
    )

    if not place_name:
        place_name = fetched_name_high or fetched_name_low or data_id

    for review in high_reviews:
        review["_sort_by"] = "ratingHigh"
    for review in low_reviews:
        review["_sort_by"] = "ratingLow"

    all_reviews = high_reviews + low_reviews
    high_count = len(high_reviews)
    low_count = len(low_reviews)
    total = high_count + low_count

    if total == 0:
        status = "partial"
        summary = f"Khong lay duoc review nao cho '{place_name}'."
    elif high_count < max_high or low_count < max_low:
        status = "partial"
        summary = f"Lay duoc {total} review cho '{place_name}' ({high_count} cao + {low_count} thap)."
    else:
        status = "success"
        summary = f"Lay duoc {total} review cho '{place_name}' ({max_high} cao nhat + {max_low} thap nhat)."

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


def review_search(place: dict[str, Any]) -> dict[str, Any]:
    """Backward-compatible alias for registry imports."""
    return search_reviews(place)


def get_place_reviews(
    data_id: str,
    max_best: int = DEFAULT_MAX_HIGH,
    max_worst: int = DEFAULT_MAX_LOW,
) -> dict[str, Any]:
    """Backward-compatible helper for tests that pass data_id directly."""
    return search_reviews(
        place={"data_id": data_id},
        max_high=max_best,
        max_low=max_worst,
    )


def search_reviews_for_places(
    places: list[dict[str, Any]],
    max_high: int = DEFAULT_MAX_HIGH,
    max_low: int = DEFAULT_MAX_LOW,
) -> list[dict[str, Any]]:
    """Lay review cho nhieu dia diem tu output cua search_places."""
    return [
        search_reviews(place, max_high=max_high, max_low=max_low)
        for place in places
        if isinstance(place, dict) and place.get("data_id")
    ]


def get_reviews_for_places(
    places: list[dict[str, Any]],
    max_best_per_place: int = DEFAULT_MAX_HIGH,
    max_worst_per_place: int = DEFAULT_MAX_LOW,
) -> list[dict[str, Any]]:
    """Backward-compatible batch alias used by older tests."""
    results = search_reviews_for_places(
        places,
        max_high=max_best_per_place,
        max_low=max_worst_per_place,
    )
    for result in results:
        result.setdefault("place_title", result.get("place_name"))
    return results


def _fetch_reviews(
    data_id: str,
    api_key: str,
    sort_by: str,
    max_count: int,
) -> tuple[list[dict[str, Any]], str]:
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
    except requests.RequestException:
        return [], ""
    except ValueError:
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

    return [_normalize_review(review) for review in raw_reviews[:max_count]], fetched_name


def _normalize_review(review: dict[str, Any]) -> dict[str, Any]:
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
        "text": review.get("snippet") or review.get("text") or None,
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
