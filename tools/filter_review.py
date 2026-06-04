"""Tool filter_reviews.

Mục đích: lọc và xếp hạng địa điểm dựa trên nhu cầu người dùng và review đã đọc.

Input:
- user_request: str
- places_with_reviews: list[dict]

Tool này không gọi API. Nó dùng scoring đơn giản, minh bạch để demo luồng:
search place -> đọc review -> lọc review -> planner trả gợi ý.
"""

from __future__ import annotations

from typing import Any


POSITIVE_TERMS = [
    "sạch",
    "đẹp",
    "vui",
    "rộng",
    "thoáng",
    "an toàn",
    "phù hợp",
    "thân thiện",
    "ngon",
    "dịch vụ tốt",
    "trẻ em",
    "gia đình",
    "nhóm bạn",
    "yên tĩnh",
]

NEGATIVE_TERMS = [
    "đông",
    "ồn",
    "bẩn",
    "đắt",
    "chật",
    "tệ",
    "khó tìm",
    "khó gửi xe",
    "phục vụ kém",
]


TOOL_DEFINITION = {
    "name": "filter_reviews",
    "description": "Lọc/xếp hạng địa điểm theo nhu cầu user dựa trên rating và nội dung review.",
    "input_schema": {
        "type": "object",
        "properties": {
            "user_request": {"type": "string"},
            "places_with_reviews": {"type": "array"},
        },
        "required": ["user_request", "places_with_reviews"],
    },
}


def filter_reviews(user_request: str, places_with_reviews: list[dict[str, Any]]) -> dict[str, Any]:
    if not places_with_reviews:
        return {
            "tool_name": "filter_reviews",
            "status": "unavailable",
            "summary": "Chưa có địa điểm/review để lọc.",
            "ranked_places": [],
            "verified": False,
        }

    ranked = [_score_place(user_request, item) for item in places_with_reviews]
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return {
        "tool_name": "filter_reviews",
        "status": "success" if any(item["review_status"] == "success" for item in ranked) else "partial",
        "summary": f"Đã xếp hạng {len(ranked)} địa điểm theo nhu cầu và review có sẵn.",
        "ranked_places": ranked,
        "verified": any(item["review_status"] == "success" for item in ranked),
    }


def _score_place(user_request: str, item: dict[str, Any]) -> dict[str, Any]:
    place = item.get("place") or {}
    reviews = item.get("reviews") or []
    review_status = str(item.get("status") or "unknown")
    request_terms = _extract_request_terms(user_request)
    text_blob = " ".join(str(review.get("text") or "").lower() for review in reviews)

    base_rating = _safe_float(place.get("rating"), default=0.0)
    score = base_rating * 10
    matched_terms = [term for term in request_terms if term in text_blob or term in str(place).lower()]
    positive_hits = [term for term in POSITIVE_TERMS if term in text_blob]
    negative_hits = [term for term in NEGATIVE_TERMS if term in text_blob]

    score += len(matched_terms) * 4
    score += len(positive_hits) * 2
    score -= len(negative_hits) * 3
    if review_status != "success":
        score -= 8

    return {
        "title": place.get("title"),
        "address": place.get("address"),
        "type": place.get("type"),
        "rating": place.get("rating"),
        "review_count": place.get("reviews"),
        "review_status": review_status,
        "score": round(score, 2),
        "matched_terms": matched_terms[:6],
        "positive_signals": positive_hits[:6],
        "negative_signals": negative_hits[:6],
        "review_evidence": [review.get("text") for review in reviews[:3] if review.get("text")],
        "data_id": place.get("data_id"),
    }


def _extract_request_terms(user_request: str) -> list[str]:
    text = user_request.lower()
    candidates = [
        "gia đình",
        "trẻ em",
        "bé",
        "nhóm bạn",
        "vui",
        "cafe",
        "cà phê",
        "thiên nhiên",
        "công viên",
        "văn hóa",
        "bảo tàng",
        "ăn uống",
        "chay",
        "an toàn",
        "yên tĩnh",
        "rẻ",
        "đẹp",
        "cuối tuần",
    ]
    return [term for term in candidates if term in text]


def _safe_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
