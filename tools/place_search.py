"""Tool search_places.

Mục đích: tìm địa điểm trên Google Maps giống như khi người dùng gõ một câu vào
ô search bar, ví dụ "quán phở ngon gần Hồ Gươm", "cafe yên tĩnh ở Tây Hồ" hoặc
"chỗ đi chơi phù hợp trẻ em ở Hà Nội".

Input duy nhất:
- query: str

Tool dùng SerpAPI Google Maps engine nếu có `SERPAPI_API_KEY` trong môi trường.
Nếu chưa có key hoặc API lỗi, tool trả kết quả có cấu trúc và nói rõ trạng thái,
không bịa dữ liệu.
"""

from __future__ import annotations

import os
from typing import Any

import requests


SERPAPI_URL = "https://serpapi.com/search"
DEFAULT_MAX_RESULTS = 6


TOOL_DEFINITION = {
    "name": "search_places",
    "description": (
        "Tìm quán ăn, cafe, chỗ chill, điểm vui chơi hoặc hoạt động ngắn hạn "
        "trên Google Maps bằng một chuỗi query giống ô tìm kiếm Google Maps."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "Câu tìm kiếm tự nhiên, nên gồm loại địa điểm và khu vực. "
                    "Ví dụ: 'quán chay gần phố cổ Hà Nội', 'cafe yên tĩnh ở Tây Hồ'."
                ),
            },
        },
        "required": ["query"],
    },
}


def search_places(query: str) -> dict[str, Any]:
    """Tìm địa điểm trên Google Maps bằng đúng một chuỗi query.

    Parameters
    ----------
    query:
        Câu tìm kiếm tự nhiên, giống nội dung nhập vào search bar Google Maps.

    Returns
    -------
    dict
        Kết quả chuẩn hóa gồm `tool_name`, `status`, `summary`, `places`,
        `verified`.
    """
    normalized_query = " ".join(str(query).split())
    if not normalized_query:
        return _error_result("Query rỗng. Cần một chuỗi tìm kiếm địa điểm.")

    api_key = os.getenv("SERPAPI_API_KEY", "").strip()
    placeholder_keys = {"optional_for_future_tools", "optional_for_live_place_and_review_tools"}
    if not api_key or api_key in placeholder_keys:
        return {
            "tool_name": "search_places",
            "status": "unavailable",
            "summary": "Chưa có SERPAPI_API_KEY nên chưa thể tìm Google Maps thật.",
            "query": normalized_query,
            "places": [],
            "verified": False,
        }

    try:
        response = requests.get(
            SERPAPI_URL,
            params={
                "engine": "google_maps",
                "q": normalized_query,
                "type": "search",
                "hl": "vi",
                "api_key": api_key,
            },
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return _error_result(f"Lỗi khi gọi SerpAPI Google Maps: {exc}", normalized_query)

    data = response.json()
    if data.get("error"):
        return _error_result(str(data["error"]), normalized_query)

    raw_places = data.get("local_results") or data.get("place_results") or []
    if isinstance(raw_places, dict):
        raw_places = [raw_places]

    places = [_normalize_place(place) for place in raw_places[:DEFAULT_MAX_RESULTS]]
    return {
        "tool_name": "search_places",
        "status": "success",
        "summary": f"Tìm thấy {len(places)} địa điểm cho query: {normalized_query}",
        "query": normalized_query,
        "places": places,
        "verified": True,
    }


def search_attractions(user_request: str) -> dict[str, Any]:
    """Wrapper cho registry: tìm điểm tham quan bằng một chuỗi request."""
    result = search_places(user_request)
    result["tool_name"] = "search_attractions"
    if result["status"] == "success":
        result["summary"] = f"Tìm điểm tham quan theo Google Maps query: {result['query']}"
    return result


def _normalize_place(place: dict[str, Any]) -> dict[str, Any]:
    # SerpAPI local_results không có field 'photos', thay vào đó dùng thumbnail
    images = []

    # Collect available images/thumbnails
    if place.get("thumbnail"):
        images.append({
            "url": place.get("thumbnail"),
            "source": "Google Maps"
        })

    if place.get("serpapi_thumbnail"):
        images.append({
            "url": place.get("serpapi_thumbnail"),
            "source": "SerpAPI"
        })

    return {
        "title": place.get("title"),
        "address": place.get("address"),
        "rating": place.get("rating"),
        "reviews": place.get("reviews"),
        "price": place.get("price"),
        "type": place.get("type"),
        "open_state": place.get("open_state"),
        "phone": place.get("phone"),
        "data_id": place.get("data_id"),
        "gps": place.get("gps_coordinates"),
        "images": images,
        "photos_link": place.get("photos_link"),  # Link để fetch ảnh đầy đủ sau
    }


def _error_result(message: str, query: str | None = None) -> dict[str, Any]:
    return {
        "tool_name": "search_places",
        "status": "error",
        "summary": message,
        "query": query,
        "places": [],
        "verified": False,
    }
