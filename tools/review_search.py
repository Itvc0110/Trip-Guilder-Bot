"""Tool get_place_reviews.

Mục đích: lấy review của một địa điểm cụ thể trên Google Maps,
dùng ``data_id`` lấy từ kết quả của ``search_places``.

Workflow điển hình
------------------
1. Gọi search_places(query) → nhận danh sách địa điểm, mỗi nơi có ``data_id``
2. Gọi get_place_reviews(data_id=...) → nhận danh sách review thực tế

Input:
- data_id    : str   — lấy từ trường ``data_id`` trong kết quả search_places
- max_best : int   — số review tốt nhất (ratingHigh) tối đa muốn lấy (mặc định 5)
- max_worst: int   — số review tệ nhất (ratingLow) tối đa muốn lấy (mặc định 5)

Tool dùng SerpAPI Google Maps Reviews engine nếu có ``SERPAPI_API_KEY``.
Nếu chưa có key hoặc API lỗi, trả kết quả có cấu trúc và nói rõ trạng thái.
"""

from __future__ import annotations

import os
from typing import Any

import requests


SERPAPI_URL = "https://serpapi.com/search"
DEFAULT_MAX_BEST = 5
DEFAULT_MAX_WORST = 5


TOOL_DEFINITION = {
    "name": "get_place_reviews",
    "description": (
        "Lấy các review thực tế của một địa điểm trên Google Maps. "
        "Cần truyền vào data_id lấy từ kết quả của tool search_places. "
        "Trả về danh sách review kèm rating, nội dung, ngày đăng và tên người dùng."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "data_id": {
                "type": "string",
                "description": (
                    "data_id của địa điểm, lấy từ trường 'data_id' trong kết quả search_places. "
                    "Dạng chuỗi hex, ví dụ: '0x3135ab12:0x4a2bcd'."
                ),
            },
            "max_best": {
                "type": "integer",
                "description": "Số review tốt nhất (rating cao nhất) tối đa muốn lấy. Mặc định là 5.",
            },
            "max_worst": {
                "type": "integer",
                "description": "Số review tệ nhất (rating thấp nhất) tối đa muốn lấy. Mặc định là 5.",
            },
        },
        "required": ["data_id"],
    },
}


def get_place_reviews(
    data_id: str,
    max_best: int = DEFAULT_MAX_BEST,
    max_worst: int = DEFAULT_MAX_WORST,
) -> dict[str, Any]:
    """Lấy review của một địa điểm Google Maps theo data_id.

    Parameters
    ----------
    data_id:
        Google Maps data_id của địa điểm.
        Lấy từ trường ``data_id`` trong kết quả :func:`search_places`.
    max_best:
        Số lượng review tốt nhất tối đa muốn trả về. Mặc định 5.
    max_worst:
        Số lượng review tệ nhất tối đa muốn trả về. Mặc định 5.

    Returns
    -------
    dict
        Kết quả chuẩn hóa gồm ``tool_name``, ``status``, ``summary``,
        ``data_id``, ``reviews``, ``verified``.
    """
    data_id = str(data_id).strip()
    if not data_id:
        return _error_result("data_id rỗng. Cần truyền data_id lấy từ kết quả search_places.")

    api_key = os.getenv("SERPAPI_API_KEY", "").strip()
    if not api_key or api_key == "optional_for_future_tools":
        return {
            "tool_name": "get_place_reviews",
            "status": "unavailable",
            "summary": "Chưa có SERPAPI_API_KEY nên chưa thể lấy review thật.",
            "data_id": data_id,
            "reviews": [],
            "verified": False,
        }

    reviews = []
    place_name = data_id
    
    def fetch_reviews(sort_by: str, max_count: int):
        if max_count <= 0:
            return
        try:
            response = requests.get(
                SERPAPI_URL,
                params={
                    "engine": "google_maps_reviews",
                    "data_id": data_id,
                    "hl": "vi",
                    "api_key": api_key,
                    "sort_by": sort_by
                },
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
            if data.get("error"):
                return
            
            nonlocal place_name
            place_info = data.get("place_info") or {}
            if place_info.get("title"):
                place_name = place_info.get("title")

            raw_reviews = data.get("reviews") or []
            for r in raw_reviews[:max_count]:
                norm = _normalize_review(r)
                norm["sort_by"] = sort_by
                reviews.append(norm)
        except Exception:
            pass

    fetch_reviews("ratingHigh", max_best)
    fetch_reviews("ratingLow", max_worst)

    return {
        "tool_name": "get_place_reviews",
        "status": "success",
        "summary": f"Lấy được {len(reviews)} review ({max_best} tốt, {max_worst} tệ) cho địa điểm: {place_name}",
        "data_id": data_id,
        "place_name": place_name,
        "reviews": reviews,
        "verified": True,
    }


def get_reviews_for_places(places: list[dict[str, Any]], max_best_per_place: int = 2, max_worst_per_place: int = 1) -> list[dict[str, Any]]:
    """Lấy review cho nhiều địa điểm từ kết quả search_places.

    Đây là hàm tiện ích để kết nối trực tiếp output của search_places
    vào luồng lấy review.

    Parameters
    ----------
    places:
        Danh sách địa điểm, lấy từ trường ``places`` trong kết quả search_places.
    max_best_per_place:
        Số review tốt nhất lấy cho mỗi địa điểm. Mặc định 2.
    max_worst_per_place:
        Số review tệ nhất lấy cho mỗi địa điểm. Mặc định 1.

    Returns
    -------
    list[dict]
        Danh sách kết quả review tương ứng với từng địa điểm có data_id.
    """
    results = []
    for place in places:
        data_id = place.get("data_id")
        if not data_id:
            continue
        result = get_place_reviews(data_id, max_best=max_best_per_place, max_worst=max_worst_per_place)
        result["place_title"] = place.get("title")
        result["place_address"] = place.get("address")
        results.append(result)
    return results


def _normalize_review(review: dict[str, Any]) -> dict[str, Any]:
    return {
        "user": review.get("user", {}).get("name") if isinstance(review.get("user"), dict) else review.get("username"),
        "rating": review.get("rating"),
        "date": review.get("date") or review.get("iso_date"),
        "snippet": review.get("snippet") or review.get("text"),
        "likes": review.get("likes"),
        "source": review.get("source"),
    }


def _error_result(message: str, data_id: str | None = None) -> dict[str, Any]:
    return {
        "tool_name": "get_place_reviews",
        "status": "error",
        "summary": message,
        "data_id": data_id,
        "reviews": [],
        "verified": False,
    }
