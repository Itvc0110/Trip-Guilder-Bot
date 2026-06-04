"""Registry cho active tools của DiChoiBot.

Luồng chính hiện tại:
1. `search_places(query)`: tìm địa điểm bằng một query kiểu Google Maps.
2. `review_search(place)`: đọc review cho từng địa điểm, ưu tiên `data_id`.
3. `filter_reviews(user_request, places_with_reviews)`: xếp hạng địa điểm theo
   nhu cầu người dùng và review.

Tên `run_placeholder_tools` được giữ để tương thích với `agent.py`, nhưng hàm
này đang chạy pipeline thật/available theo tool hiện có.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Callable

from tools.filter_review import TOOL_DEFINITION as FILTER_REVIEWS_DEFINITION
from tools.filter_review import filter_reviews
from tools.place_search import TOOL_DEFINITION as SEARCH_PLACES_DEFINITION
from tools.place_search import search_attractions, search_places
from tools.review_search import TOOL_DEFINITION as REVIEW_SEARCH_DEFINITION
from tools.review_search import review_search, search_reviews


ToolFn = Callable[..., dict[str, Any]]


ACTIVE_PIPELINE = ["search_places", "review_search", "filter_reviews"]


TOOL_REGISTRY: dict[str, ToolFn] = {
    "search_places": search_places,
    "review_search": review_search,
    "search_reviews": search_reviews,
    "filter_reviews": filter_reviews,
    # Backward-compatible alias. The active router should prefer search_places.
    "search_attractions": search_attractions,
}


TOOL_DEFINITIONS = {
    "search_places": SEARCH_PLACES_DEFINITION,
    "review_search": REVIEW_SEARCH_DEFINITION,
    "search_reviews": REVIEW_SEARCH_DEFINITION,
    "filter_reviews": FILTER_REVIEWS_DEFINITION,
}


@dataclass
class RequestForm:
    raw_request: str
    place_type: str | None
    location: str | None
    search_query: str
    preferences: list[str]
    constraints: list[str]
    optional_context: list[str]
    missing_required: list[str]


def run_placeholder_tools(route: dict[str, Any], user_request: str) -> list[dict[str, Any]]:
    """Run DiChoiBot's place/review/filter pipeline.

    If router returns `plan`, run the canonical pipeline regardless of aliases in
    `tools_to_use`. If router does not return `plan`, return no findings.
    """
    if route.get("decision") != "plan":
        return []

    findings: list[dict[str, Any]] = []
    request_form = build_request_form(user_request)
    findings.append(
        {
            "tool_name": "request_form",
            "status": "success" if not request_form.missing_required else "partial",
            "summary": f"Đã tách request thành search_query: {request_form.search_query}",
            "form": asdict(request_form),
            "verified": True,
        }
    )

    place_result = search_places(request_form.search_query)
    findings.append(place_result)

    places = place_result.get("places") or []
    places_with_reviews: list[dict[str, Any]] = []

    if not places:
        findings.append(
            {
                "tool_name": "review_search",
                "status": "unavailable",
                "summary": "Chưa có địa điểm từ search_places nên chưa thể đọc review.",
                "place": None,
                "reviews": [],
                "verified": False,
            }
        )
    else:
        for place in places:
            review_result = review_search(place)
            findings.append(review_result)
            places_with_reviews.append(
                {
                    "place": place,
                    "status": review_result.get("status"),
                    "reviews": review_result.get("reviews") or [],
                    "review_summary": review_result.get("summary"),
                }
            )

    filter_request = build_filter_request(request_form)
    findings.append(filter_reviews(filter_request, places_with_reviews))
    return findings


def get_tool(tool_name: str) -> ToolFn | None:
    """Return a registered tool by name."""
    return TOOL_REGISTRY.get(tool_name)


def build_request_form(user_request: str) -> RequestForm:
    """Extract a tool-ready form from the user's natural-language request.

    Required for search: place_type + location. Preferences/constraints are used
    for filter/personalization and should not block tool search.
    """
    text = normalize_text(user_request)
    place_type = extract_place_type(text)
    location = extract_location(text)
    preferences = extract_terms(text, PREFERENCE_TERMS)
    constraints = extract_terms(text, CONSTRAINT_TERMS)
    optional_context = extract_terms(text, OPTIONAL_CONTEXT_TERMS)

    missing_required = []
    if not place_type:
        missing_required.append("place_type")
    if not location:
        missing_required.append("location")

    search_query = build_search_query(place_type, location, text)
    return RequestForm(
        raw_request=user_request,
        place_type=place_type,
        location=location,
        search_query=search_query,
        preferences=preferences,
        constraints=constraints,
        optional_context=optional_context,
        missing_required=missing_required,
    )


PLACE_TYPE_PATTERNS = [
    (r"\b(cafe|coffee|cà phê|ca phe|quán cà phê|quan ca phe)\b", "cafe"),
    (r"\b(quán ăn|quan an|nhà hàng|nha hang|ăn|an|đồ ăn|do an)\b", "quán ăn"),
    (r"\b(quán chay|quan chay|ăn chay|an chay)\b", "quán chay"),
    (r"\b(chỗ chill|cho chill|chill)\b", "chỗ chill"),
    (r"\b(công viên|cong vien)\b", "công viên"),
    (r"\b(bảo tàng|bao tang)\b", "bảo tàng"),
    (r"\b(khu vui chơi|địa điểm đi chơi|dia diem di choi|chỗ chơi|cho choi)\b", "địa điểm đi chơi"),
]

LOCATION_PATTERNS = [
    r"(?:gần|gan|gaanf|ở|o|quanh|khu vực|khu vuc|tại|tai)\s+([^,.;!?]+)",
]

KNOWN_LOCATIONS = [
    "vinuni",
    "vin university",
    "vinhome ocean park",
    "ocean park",
    "tây hồ",
    "tay ho",
    "hồ gươm",
    "ho guom",
    "hoàn kiếm",
    "hoan kiem",
    "cầu giấy",
    "cau giay",
    "đống đa",
    "dong da",
    "hà nội",
    "ha noi",
    "sài gòn",
    "sai gon",
    "tp hcm",
    "đà nẵng",
    "da nang",
]

PREFERENCE_TERMS = [
    "yên tĩnh",
    "yen tinh",
    "đẹp",
    "dep",
    "view đẹp",
    "view dep",
    "chill",
    "ấm cúng",
    "am cung",
    "rộng",
    "rong",
    "thoáng",
    "thoang",
    "nhiều review tốt",
    "review tốt",
    "an toàn",
    "an toan",
    "phù hợp trẻ em",
    "phu hop tre em",
    "gia đình",
    "gia dinh",
    "nhóm bạn",
    "nhom ban",
]

CONSTRAINT_TERMS = [
    "không quá đông",
    "khong qua dong",
    "ít đông",
    "it dong",
    "không ồn",
    "khong on",
    "dễ gửi xe",
    "de gui xe",
    "giá rẻ",
    "gia re",
    "rẻ",
    "re",
    "ăn chay",
    "an chay",
    "không hút thuốc",
    "khong hut thuoc",
]

OPTIONAL_CONTEXT_TERMS = [
    "cuối tuần",
    "cuoi tuan",
    "buổi tối",
    "buoi toi",
    "hẹn hò",
    "hen ho",
    "làm việc",
    "lam viec",
    "sống ảo",
    "song ao",
]


def normalize_text(text: str) -> str:
    return " ".join(str(text).lower().split())


def extract_place_type(text: str) -> str | None:
    for pattern, value in PLACE_TYPE_PATTERNS:
        if re.search(pattern, text):
            return value
    return None


def extract_location(text: str) -> str | None:
    for known in KNOWN_LOCATIONS:
        if known in text:
            return canonical_location(known)

    for pattern in LOCATION_PATTERNS:
        match = re.search(pattern, text)
        if match:
            location = clean_location(match.group(1))
            if location:
                return location
    return None


def canonical_location(location: str) -> str:
    aliases = {
        "vin university": "VinUni",
        "vinuni": "VinUni",
        "vinhome ocean park": "Vinhomes Ocean Park",
        "ocean park": "Vinhomes Ocean Park",
        "tay ho": "Tây Hồ",
        "tây hồ": "Tây Hồ",
        "ho guom": "Hồ Gươm",
        "hồ gươm": "Hồ Gươm",
        "ha noi": "Hà Nội",
        "hà nội": "Hà Nội",
        "cau giay": "Cầu Giấy",
        "cầu giấy": "Cầu Giấy",
        "hoan kiem": "Hoàn Kiếm",
        "hoàn kiếm": "Hoàn Kiếm",
        "dong da": "Đống Đa",
        "đống đa": "Đống Đa",
        "sai gon": "Sài Gòn",
        "sài gòn": "Sài Gòn",
        "tp hcm": "TP HCM",
        "da nang": "Đà Nẵng",
        "đà nẵng": "Đà Nẵng",
    }
    return aliases.get(location, location.strip())


def clean_location(location: str) -> str:
    stop_words = PREFERENCE_TERMS + CONSTRAINT_TERMS + OPTIONAL_CONTEXT_TERMS
    cleaned = location.strip()
    for stop in stop_words:
        index = cleaned.find(stop)
        if index > 0:
            cleaned = cleaned[:index].strip()
    cleaned = re.sub(r"\b(yên tĩnh|đẹp|chill|rẻ|an toàn)\b.*$", "", cleaned).strip()
    return cleaned[:80].strip(" ,.-")


def extract_terms(text: str, terms: list[str]) -> list[str]:
    matched: list[str] = []
    for term in sorted(terms, key=len, reverse=True):
        pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
        if re.search(pattern, text) and not any(term in existing for existing in matched):
            matched.append(term)
    return list(reversed(matched))


def build_search_query(place_type: str | None, location: str | None, text: str) -> str:
    if place_type and location:
        return f"{place_type} gần {location}"
    if place_type:
        return place_type
    if location:
        return f"địa điểm đi chơi gần {location}"
    return text


def build_filter_request(form: RequestForm) -> str:
    parts = [form.raw_request]
    if form.preferences:
        parts.append("Ưu tiên: " + ", ".join(form.preferences))
    if form.constraints:
        parts.append("Ràng buộc: " + ", ".join(form.constraints))
    if form.optional_context:
        parts.append("Bối cảnh thêm: " + ", ".join(form.optional_context))
    return "\n".join(parts)
