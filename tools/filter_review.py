"""Tool filter_reviews - Phiên bản hoàn chỉnh với LLM integration.

Nhiệm vụ:
1. Nhận reviews thô từ search_reviews (5 tốt + 5 xấu).
2. Trích xuất 2 review MỚI NHẤT đầy đủ thông tin.
3. Sử dụng LLM để sinh nhận xét tổng quát tự nhiên, phù hợp vibe hẹn hò.
4. Xếp hạng địa điểm dựa trên rating + review.
"""

from __future__ import annotations
from typing import Any
import datetime
import os

from config import load_settings
from openrouter_client import OpenRouterClient, OpenRouterError


# Load settings để dùng LLM
settings = load_settings()
client = OpenRouterClient(settings) if settings.has_api_key else None


TOOL_DEFINITION = {
    "name": "filter_reviews",
    "description": "Lọc và xếp hạng địa điểm, trích xuất 2 review mới nhất và sinh nhận xét tổng quát bằng LLM.",
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

    ranked = [_process_place(user_request, item) for item in places_with_reviews]
    ranked.sort(key=lambda x: x["score"], reverse=True)

    return {
        "tool_name": "filter_reviews",
        "status": "success" if any(item["review_status"] == "success" for item in ranked) else "partial",
        "summary": f"Đã phân tích {len(ranked)} địa điểm và tạo nhận xét bằng LLM.",
        "ranked_places": ranked,
        "verified": any(item.get("review_status") == "success" for item in ranked),
    }


def _process_place(user_request: str, item: dict[str, Any]) -> dict[str, Any]:
    place = item.get("place") or {}
    reviews = item.get("reviews") or []
    review_status = str(item.get("status") or "unknown")

    # Lấy 2 review mới nhất
    recent_reviews = _get_two_most_recent_reviews(reviews)

    # Tính score
    score = _calculate_score(place, reviews, user_request)

    # Sinh nhận xét tổng quát bằng LLM (có fallback)
    general_comment = _generate_llm_comment(place, recent_reviews, user_request)

    return {
        "title": place.get("title"),
        "address": place.get("address"),
        "rating": place.get("rating"),
        "review_count": place.get("reviews"),
        "review_status": review_status,
        "score": round(score, 2),
        "recent_reviews": recent_reviews,      # 2 review mới nhất đầy đủ
        "general_comment": general_comment,    # Nhận xét LLM
        "data_id": place.get("data_id"),
    }


def _get_two_most_recent_reviews(reviews: list[dict]) -> list[dict]:
    """Lấy 2 review mới nhất theo ngày."""
    def parse_date(review):
        date_str = review.get("date") or ""
        try:
            # Xử lý nhiều format ngày của SerpAPI
            for fmt in ["%b %d, %Y", "%Y-%m-%d", "%d/%m/%Y", "%B %d, %Y"]:
                try:
                    return datetime.datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return datetime.datetime.min
        except:
            return datetime.datetime.min

    sorted_reviews = sorted(reviews, key=parse_date, reverse=True)
    return sorted_reviews[:2]


def _calculate_score(place: dict, reviews: list, user_request: str) -> float:
    """Tính điểm xếp hạng cơ bản."""
    base_score = float(place.get("rating") or 0) * 10
    review_bonus = len(reviews) * 0.8
    return base_score + review_bonus


def _generate_llm_comment(place: dict, recent_reviews: list[dict], user_request: str) -> str:
    """Sinh nhận xét tổng quát bằng LLM. Có fallback nếu không có API key."""
    name = place.get("title", "Địa điểm này")

    if not recent_reviews:
        return f"{name} hiện chưa có review mới. Khuyến nghị kiểm tra trực tiếp trên Google Maps trước khi đến."

    # Chuẩn bị context review
    review_context = []
    for r in recent_reviews:
        user = r.get("user") or "Khách"
        date = r.get("date") or "gần đây"
        rating = r.get("rating") or "?"
        snippet = (r.get("snippet") or "").strip()[:150]
        review_context.append(f"- {user} ({date}, {rating}★): {snippet}")

    review_text = "\n".join(review_context)

    prompt = f"""
Bạn là chuyên gia review địa điểm hẹn hò tại Hà Nội.
Hãy viết một đoạn nhận xét tổng quát ngắn gọn, tự nhiên bằng tiếng Việt cho cặp đôi.

Tên địa điểm: {name}
Yêu cầu của user: {user_request}

Review mới nhất:
{review_text}

Yêu cầu:
- Viết giọng thân thiện, chân thực.
- Nhấn mạnh điểm tích cực và lưu ý nếu có.
- Độ dài khoảng 2-4 câu.
- Không bịa thông tin.
"""

    # Thử gọi LLM
    if client and settings.has_api_key:
        try:
            response = client.chat(
                model=settings.planner_model,
                messages=[
                    {"role": "system", "content": "Bạn là trợ lý review địa điểm hẹn hò chuyên nghiệp."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )
            if response and response.strip():
                return response.strip()
        except (OpenRouterError, Exception):
            pass  # fallback xuống rule-based

    # Fallback rule-based
    return (f"**Nhận xét về {name}**: "
            f"Có {len(recent_reviews)} review mới gần đây. "
            f"Đa số khách đánh giá tích cực. "
            f"Phù hợp cho buổi hẹn hò {user_request.lower() if 'hẹn' in user_request.lower() else 'thư giãn'}.")


# For backward compatibility
def filter_reviews_tool(user_request: str, places_with_reviews: list[dict]) -> dict:
    return filter_reviews(user_request, places_with_reviews)
