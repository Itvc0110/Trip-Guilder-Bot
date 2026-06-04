"""Tool search_reviews.

Mục đích: đọc review của một địa điểm đã tìm được từ `search_places`.

Input:
- place_result: dict | str

Ưu tiên dùng `data_id` từ kết quả Google Maps/SerpAPI. Nếu chưa có
`SERPAPI_API_KEY`, thiếu `data_id`, hoặc API lỗi, tool trả trạng thái rõ ràng và
không bịa review.
"""

from __future__ import annotations

import os
from typing import Any

import requests


SERPAPI_URL = "https://serpapi.com/search"
DEFAULT_MAX_REVIEWS = 8


TOOL_DEFINITION = {
    "name": "search_reviews",
    "description": "Lấy review Google Maps của một địa điểm, ưu tiên data_id từ search_places.",
    "input_schema": {
        "type": "object",
        "properties": {
            "place_result": {
                "type": ["object", "string"],
                "description": "Một place dict từ search_places hoặc chuỗi data_id/tên địa điểm.",
            },
        },
        "required": ["place_result"],
    },
}


def search_reviews(place_result: dict[str, Any] | str) -> dict[str, Any]:
    place = _normalize_input(place_result)
    api_key = os.getenv("SERPAPI_API_KEY", "").strip()
    if not api_key or api_key == "optional_for_future_tools":
        return {
            "tool_name": "search_reviews",
            "status": "unavailable",
            "summary": "Chưa có SERPAPI_API_KEY nên chưa thể đọc review thật.",
            "place": place,
            "reviews": [],
            "verified": False,
        }

    data_id = place.get("data_id")
    if not data_id:
        return {
            "tool_name": "search_reviews",
            "status": "unavailable",
            "summary": "Địa điểm chưa có data_id nên chưa thể gọi Google Maps reviews.",
            "place": place,
            "reviews": [],
            "verified": False,
        }

    try:
        response = requests.get(
            SERPAPI_URL,
            params={
                "engine": "google_maps_reviews",
                "data_id": data_id,
                "hl": "vi",
                "api_key": api_key,
            },
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return _error_result(f"Lỗi khi gọi SerpAPI review: {exc}", place)

    data = response.json()
    if data.get("error"):
        return _error_result(str(data["error"]), place)

    raw_reviews = data.get("reviews") or []
    reviews = [_normalize_review(review) for review in raw_reviews[:DEFAULT_MAX_REVIEWS]]
    return {
        "tool_name": "search_reviews",
        "status": "success",
        "summary": f"Đọc được {len(reviews)} review cho {place.get('title') or data_id}.",
        "place": place,
        "reviews": reviews,
        "verified": True,
    }


def _normalize_input(place_result: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(place_result, dict):
        return {
            "title": place_result.get("title"),
            "address": place_result.get("address"),
            "rating": place_result.get("rating"),
            "reviews": place_result.get("reviews"),
            "type": place_result.get("type"),
            "data_id": place_result.get("data_id"),
            "gps": place_result.get("gps"),
        }
    text = str(place_result).strip()
    return {"title": text, "data_id": text if text.startswith("0x") else None}


def _normalize_review(review: dict[str, Any]) -> dict[str, Any]:
    return {
        "rating": review.get("rating"),
        "text": review.get("snippet") or review.get("text"),
        "date": review.get("date"),
        "user": (review.get("user") or {}).get("name") if isinstance(review.get("user"), dict) else review.get("user"),
        "likes": review.get("likes"),
    }


def _error_result(message: str, place: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool_name": "search_reviews",
        "status": "error",
        "summary": message,
        "place": place,
        "reviews": [],
        "verified": False,
    }
