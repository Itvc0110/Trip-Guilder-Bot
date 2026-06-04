"""Tool search_reviews — Đọc review thực tế cho một địa điểm từ Google Maps.

Vị trí trong pipeline:
    search_places  →  search_reviews  →  filter_reviews

Hàm chính được registry.py gọi:
    search_reviews(place: dict) -> dict

Input (place dict từ search_places):
    - data_id   : str  — bắt buộc, Google Maps data_id
    - title     : str  — tên địa điểm, dùng cho summary log
    - address   : str  — địa chỉ, dùng cho summary log

Logic lấy review:
    - 2 lần gọi SerpAPI Google Maps Reviews engine:
        1. sort_by=ratingHigh  → tối đa 5 review (review đánh giá cao nhất)
        2. sort_by=ratingLow   → tối đa 5 review (review đánh giá thấp nhất)
    - Không lọc, không bịa, không chỉnh sửa nội dung
    - Trả nguyên dữ liệu thực từ API cho filter_reviews xử lý tiếp

Nguyên tắc không bịa:
    - Nếu thiếu SERPAPI_API_KEY → status=unavailable, reviews=[]
    - Nếu API lỗi / timeout     → status=error, reviews=[]
    - Không bao giờ tự tạo snippet, rating, tên user

Output:
    dict với các trường:
        tool_name   : "search_reviews"
        status      : "success" | "partial" | "unavailable" | "error"
        summary     : mô tả kết quả (số review lấy được, tên địa điểm)
        place_name  : tên địa điểm
        place_addr  : địa chỉ địa điểm
        data_id     : data_id đã dùng
        reviews     : list[dict] — danh sách review, trường xem _normalize_review()
        high_count  : số review cao (ratingHigh) thực tế lấy được
        low_count   : số review thấp (ratingLow) thực tế lấy được
        verified    : bool
"""

from __future__ import annotations

import os
from typing import Any

import requests


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SERPAPI_URL = "https://serpapi.com/search"

# Số review tối đa mỗi chiều — giá trị mặc định theo yêu cầu: 5 cao + 5 thấp
DEFAULT_MAX_HIGH = 5
DEFAULT_MAX_LOW = 5

# Tool definition cho agent registry / Claude tool_use schema
TOOL_DEFINITION = {
    "name": "search_reviews",
    "description": (
        "Lấy review thực tế của một địa điểm Google Maps: "
        f"{DEFAULT_MAX_HIGH} review đánh giá cao nhất và {DEFAULT_MAX_LOW} review đánh giá thấp nhất. "
        "Nhận place dict từ search_places. Trả về review thô để filter_reviews xử lý tiếp."
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
                "description": f"Số review đánh giá cao nhất muốn lấy. Mặc định {DEFAULT_MAX_HIGH}.",
            },
            "max_low": {
                "type": "integer",
                "description": f"Số review đánh giá thấp nhất muốn lấy. Mặc định {DEFAULT_MAX_LOW}.",
            },
        },
        "required": ["place"],
    },
}


# ---------------------------------------------------------------------------
# Public function — đây là hàm registry.py gọi trực tiếp
# ---------------------------------------------------------------------------
def search_reviews(
    place: dict[str, Any],
    max_high: int = DEFAULT_MAX_HIGH,
    max_low: int = DEFAULT_MAX_LOW,
) -> dict[str, Any]:
    """Đọc review thực tế cho một địa điểm theo data_id từ SerpAPI.

    Lấy tối đa ``max_high`` review đánh giá cao (sort_by=ratingHigh) và
    tối đa ``max_low`` review đánh giá thấp (sort_by=ratingLow) bằng 2 call
    riêng biệt đến SerpAPI Google Maps Reviews engine.

    Không lọc, không tóm tắt, không chỉnh sửa nội dung review.
    Dữ liệu thô được trả về để ``filter_reviews`` dùng tiếp.

    Parameters
    ----------
    place:
        Dict địa điểm từ ``search_places``. Cần có ``data_id``.
        Các trường ``title``, ``address`` dùng cho log, không bắt buộc.
    max_high:
        Số review đánh giá cao nhất tối đa. Mặc định 5.
    max_low:
        Số review đánh giá thấp nhất tối đa. Mặc định 5.

    Returns
    -------
    dict
        Chuẩn hoá với ``tool_name``, ``status``, ``summary``, ``place_name``,
        ``place_addr``, ``data_id``, ``reviews``, ``high_count``,
        ``low_count``, ``verified``.
    """
    if not isinstance(place, dict):
        return _error_result("place phải là dict từ kết quả search_places.")

    data_id = str(place.get("data_id") or "").strip()
    place_name = str(place.get("title") or "").strip()
    place_addr = str(place.get("address") or "").strip()
    display_name = place_name or data_id or "địa điểm không rõ tên"

    if not data_id:
        return _error_result(
            f"data_id rỗng cho địa điểm '{display_name}'. "
            "Cần data_id lấy từ kết quả search_places.",
            place_name=place_name,
            place_addr=place_addr,
        )

    # ── Kiểm tra API key ────────────────────────────────────────────────────
    api_key = os.getenv("SERPAPI_API_KEY", "").strip()
    if not api_key or api_key in ("optional_for_live_place_and_review_tools", "optional_for_future_tools"):
        return {
            "tool_name": "search_reviews",
            "status": "unavailable",
            "summary": (
                f"Chưa có SERPAPI_API_KEY — chưa thể lấy review thật cho '{display_name}'. "
                "Thêm SERPAPI_API_KEY vào .env để kích hoạt."
            ),
            "place_name": place_name,
            "place_addr": place_addr,
            "data_id": data_id,
            "reviews": [],
            "high_count": 0,
            "low_count": 0,
            "verified": False,
        }

    # ── Gọi 2 lần SerpAPI: cao + thấp ──────────────────────────────────────
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

    # Ưu tiên tên địa điểm từ SerpAPI nếu place dict chưa có
    if not place_name:
        place_name = fetched_name_high or fetched_name_low or data_id
        display_name = place_name

    # Gắn nhãn chiều để filter_reviews phân biệt khi cần
    for r in high_reviews:
        r["_sort_by"] = "ratingHigh"
    for r in low_reviews:
        r["_sort_by"] = "ratingLow"

    all_reviews = high_reviews + low_reviews
    high_count = len(high_reviews)
    low_count = len(low_reviews)
    total = high_count + low_count

    # ── Xác định status ─────────────────────────────────────────────────────
    if total == 0:
        status = "partial"
        summary = f"Không lấy được review nào cho '{display_name}' (API trả rỗng hoặc không có review)."
    elif high_count < max_high or low_count < max_low:
        status = "partial"
        summary = (
            f"Lấy được {total} review cho '{display_name}' "
            f"({high_count} cao / {low_count} thấp — "
            f"mục tiêu {max_high} cao / {max_low} thấp). "
            "Một số slot không đủ do API trả ít hơn yêu cầu."
        )
    else:
        status = "success"
        summary = (
            f"Lấy được {total} review cho '{display_name}' "
            f"({high_count} đánh giá cao nhất + {low_count} đánh giá thấp nhất)."
        )

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
# Batch helper — tiện ích cho test hoặc gọi ngoài registry
# ---------------------------------------------------------------------------
def search_reviews_for_places(
    places: list[dict[str, Any]],
    max_high: int = DEFAULT_MAX_HIGH,
    max_low: int = DEFAULT_MAX_LOW,
) -> list[dict[str, Any]]:
    """Lấy review cho nhiều địa điểm từ output của search_places.

    Parameters
    ----------
    places:
        Danh sách địa điểm, lấy từ trường ``places`` trong kết quả search_places.
    max_high:
        Số review đánh giá cao nhất lấy cho mỗi địa điểm. Mặc định 5.
    max_low:
        Số review đánh giá thấp nhất lấy cho mỗi địa điểm. Mặc định 5.

    Returns
    -------
    list[dict]
        Danh sách kết quả review tương ứng với từng địa điểm có data_id.
    """
    return [
        search_reviews(place, max_high=max_high, max_low=max_low)
        for place in places
        if isinstance(place, dict) and place.get("data_id")
    ]


# ---------------------------------------------------------------------------
# Backward-compat alias — registry cũ có thể import get_place_reviews
# ---------------------------------------------------------------------------
def get_place_reviews(
    data_id: str,
    max_best: int = DEFAULT_MAX_HIGH,
    max_worst: int = DEFAULT_MAX_LOW,
) -> dict[str, Any]:
    """Alias backward-compat với API cũ dùng data_id trực tiếp.

    Được giữ để test_review_search.py cũ không bị lỗi import.
    Registry mới dùng search_reviews(place) thay thế.
    """
    return search_reviews(
        place={"data_id": data_id},
        max_high=max_best,
        max_low=max_worst,
    )


# ---------------------------------------------------------------------------
# Internal: gọi SerpAPI một chiều (ratingHigh hoặc ratingLow)
# ---------------------------------------------------------------------------
def _fetch_reviews(
    data_id: str,
    api_key: str,
    sort_by: str,
    max_count: int,
) -> tuple[list[dict[str, Any]], str]:
    """Gọi SerpAPI Google Maps Reviews engine cho một chiều sort.

    Parameters
    ----------
    data_id:
        Google Maps data_id của địa điểm.
    api_key:
        SERPAPI_API_KEY.
    sort_by:
        ``"ratingHigh"`` hoặc ``"ratingLow"``.
    max_count:
        Số review tối đa muốn lấy từ chiều này. Nếu <= 0, bỏ qua call.

    Returns
    -------
    tuple[list[dict], str]
        (danh sách review đã chuẩn hoá, tên địa điểm từ SerpAPI hoặc "")
    """
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
    except requests.Timeout:
        return [], ""
    except requests.RequestException:
        return [], ""
    except Exception:
        return [], ""

    if data.get("error"):
        return [], ""

    # Lấy tên địa điểm từ place_info nếu có
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
    """Chuẩn hoá một review thô từ SerpAPI về schema nội bộ.

    Không thêm, không suy diễn, không sửa nội dung.
    Các trường thiếu giữ nguyên None.
    """
    # SerpAPI trả user là dict {"name": ..., "link": ...} hoặc đôi khi string
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
        # _sort_by sẽ được gắn thêm bởi search_reviews() sau khi _fetch_reviews trả về
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
