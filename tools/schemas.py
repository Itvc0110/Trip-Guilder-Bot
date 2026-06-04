"""Schema mô tả các tool đang có của DiChoiBot."""

from __future__ import annotations


ACTIVE_PIPELINE = ["search_places", "review_search", "filter_reviews"]


TOOL_SCHEMAS = [
    {
        "name": "search_places",
        "aliases": ["search_attractions"],
        "description": "Tìm quán ăn, cafe, chỗ chill hoặc địa điểm đi chơi bằng một query tự nhiên giống Google Maps search bar.",
        "input": {
            "query": "str - câu tìm kiếm, ví dụ 'cafe yên tĩnh ở Tây Hồ' hoặc 'quán ăn gần Hồ Gươm'.",
        },
        "output": {
            "tool_name": "search_places",
            "status": "success | unavailable | error",
            "summary": "str",
            "query": "str",
            "places": "list[dict] - title, address, rating, reviews, price, type, open_state, phone, data_id, gps, images",
            "verified": "bool",
        },
    },
    {
        "name": "review_search",
        "aliases": ["search_reviews", "get_place_reviews", "get_reviews_for_places"],
        "description": "Đọc review thô của một địa điểm Google Maps, ưu tiên data_id từ search_places.",
        "input": {
            "place": "dict - một địa điểm từ search_places, cần data_id nếu muốn gọi review live.",
            "max_high": "int - số review rating cao nhất, mặc định 5.",
            "max_low": "int - số review rating thấp nhất, mặc định 5.",
        },
        "output": {
            "tool_name": "search_reviews",
            "status": "success | partial | unavailable | error",
            "summary": "str",
            "place_name": "str",
            "place_addr": "str",
            "data_id": "str | None",
            "reviews": "list[dict] - user, rating, date, snippet/text, likes, source, _sort_by",
            "high_count": "int",
            "low_count": "int",
            "verified": "bool",
        },
    },
    {
        "name": "filter_reviews",
        "aliases": [],
        "description": "Xếp hạng địa điểm theo nhu cầu user và review đã đọc; có thể sinh nhận xét tổng quát bằng LLM nếu model khả dụng.",
        "input": {
            "user_request": "str - nhu cầu ban đầu của user.",
            "places_with_reviews": "list[dict] - mỗi item gồm place, status, reviews, review_summary.",
        },
        "output": {
            "tool_name": "filter_reviews",
            "status": "success | partial | unavailable",
            "summary": "str",
            "ranked_places": "list[dict] - title, address, rating, review_count, review_status, score, recent_reviews, general_comment, data_id",
            "verified": "bool",
        },
    },
]
