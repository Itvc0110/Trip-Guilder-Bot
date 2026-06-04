"""Schema mô tả active tools của scope gợi ý địa điểm theo review."""

from __future__ import annotations


TOOL_SCHEMAS = [
    {
        "name": "search_places",
        "description": "Tìm địa điểm trên Google Maps bằng một chuỗi query tự nhiên.",
        "parameters": ["query"],
    },
    {
        "name": "review_search",
        "description": "Đọc review của một địa điểm, ưu tiên data_id từ search_places.",
        "parameters": ["place_result"],
    },
    {
        "name": "filter_reviews",
        "description": "Lọc và xếp hạng địa điểm theo nhu cầu user dựa trên review.",
        "parameters": ["user_request", "places_with_reviews"],
    },
]
