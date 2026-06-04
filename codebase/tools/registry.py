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
import time
from dataclasses import asdict, dataclass
from datetime import datetime
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


def run_placeholder_tools(
    route: dict[str, Any],
    user_request: str,
    conversation_context: str = "",
    request_state: dict[str, Any] | None = None,
    tool_log: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Run DiChoiBot's place/review/filter pipeline.

    If router returns `plan`, run the canonical pipeline regardless of aliases in
    `tools_to_use`. If router does not return `plan`, return no findings.
    """
    if route.get("decision") != "plan":
        return []

    findings: list[dict[str, Any]] = []
    request_form = request_form_from_state(user_request, request_state) if request_state else build_request_form(user_request, conversation_context)
    started = time.perf_counter()
    findings.append(
        {
            "tool_name": "request_form",
            "status": "success" if not request_form.missing_required else "partial",
            "summary": f"Đã tách request thành search_query: {request_form.search_query}",
            "form": asdict(request_form),
            "verified": True,
        }
    )
    append_tool_log(
        tool_log,
        tool_name="request_form",
        tool_input={"user_request": user_request, "request_state": asdict(request_form)},
        result=findings[-1],
        started=started,
        result_count=1,
    )

    started = time.perf_counter()
    place_result = search_places(request_form.search_query)
    findings.append(place_result)
    append_tool_log(
        tool_log,
        tool_name="search_places",
        tool_input={"query": request_form.search_query},
        result=place_result,
        started=started,
        result_count=len(place_result.get("places") or []),
    )

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
        append_tool_log(
            tool_log,
            tool_name="review_search",
            tool_input={"place": None},
            result=findings[-1],
            started=time.perf_counter(),
            result_count=0,
        )
    else:
        for place in places:
            started = time.perf_counter()
            review_result = review_search(place)
            findings.append(review_result)
            append_tool_log(
                tool_log,
                tool_name="review_search",
                tool_input={
                    "title": place.get("title"),
                    "address": place.get("address"),
                    "data_id": place.get("data_id"),
                },
                result=review_result,
                started=started,
                result_count=len(review_result.get("reviews") or []),
            )
            places_with_reviews.append(
                {
                    "place": place,
                    "status": review_result.get("status"),
                    "reviews": review_result.get("reviews") or [],
                    "review_summary": review_result.get("summary"),
                }
            )

    filter_request = build_filter_request(request_form)
    started = time.perf_counter()
    filter_result = filter_reviews(filter_request, places_with_reviews)
    findings.append(filter_result)
    append_tool_log(
        tool_log,
        tool_name="filter_reviews",
        tool_input={
            "user_request": filter_request,
            "places_count": len(places_with_reviews),
        },
        result=filter_result,
        started=started,
        result_count=len(filter_result.get("ranked_places") or []),
    )
    return findings


def append_tool_log(
    tool_log: list[dict[str, Any]] | None,
    *,
    tool_name: str,
    tool_input: dict[str, Any],
    result: dict[str, Any],
    started: float,
    result_count: int,
) -> None:
    """Append one normalized tool execution log entry."""
    if tool_log is None:
        return

    status = str(result.get("status") or "unknown")
    error = result.get("summary") if status == "error" else None
    tool_log.append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "tool_name": tool_name,
            "input": tool_input,
            "status": status,
            "summary": result.get("summary"),
            "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            "verified": bool(result.get("verified")),
            "result_count": result_count,
            "error": error,
        }
    )


def request_form_from_state(user_request: str, request_state: dict[str, Any] | None) -> RequestForm:
    """Build a RequestForm from the merged session state."""
    state = request_state or {}
    place_type = normalize_optional_string(state.get("place_type"))
    location = normalize_optional_string(state.get("location"))
    preferences = normalize_string_list(state.get("preferences"))
    constraints = normalize_string_list(state.get("constraints"))
    optional_context = normalize_string_list(state.get("optional_context"))
    missing_required = []
    if not place_type:
        missing_required.append("place_type")
    if not location:
        missing_required.append("location")

    search_query = normalize_optional_string(state.get("search_query")) or build_search_query(place_type, location, user_request)
    return RequestForm(
        raw_request=str(state.get("raw_request") or user_request),
        place_type=place_type,
        location=location,
        search_query=search_query,
        preferences=preferences,
        constraints=constraints,
        optional_context=optional_context,
        missing_required=missing_required,
    )


def get_tool(tool_name: str) -> ToolFn | None:
    """Return a registered tool by name."""
    return TOOL_REGISTRY.get(tool_name)


def build_request_form(user_request: str, conversation_context: str = "") -> RequestForm:
    """Extract a tool-ready form from the user's request, incorporating past context.

    Required for search: place_type + location. Preferences/constraints are used
    for filter/personalization and should not block tool search.
    """
    text = normalize_text(user_request)
    context_text = normalize_text(conversation_context)

    # 1. Extract place_type: try current, fallback to history context
    place_type = extract_place_type(text)
    if not place_type and context_text:
        place_type = extract_place_type(context_text)

    # 2. Extract location: try current, fallback to history context
    location = extract_location(text)
    if not location and context_text:
        location = extract_location(context_text)

    # 3. Extract preferences, constraints, optional context
    preferences = extract_terms(text, PREFERENCE_TERMS)
    constraints = extract_terms(text, CONSTRAINT_TERMS)
    optional_context = extract_terms(text, OPTIONAL_CONTEXT_TERMS)

    # Merge preferences, constraints, optional context from history if not present
    if context_text:
        ctx_prefs = extract_terms(context_text, PREFERENCE_TERMS)
        for p in ctx_prefs:
            if p not in preferences:
                preferences.append(p)

        ctx_consts = extract_terms(context_text, CONSTRAINT_TERMS)
        for c in ctx_consts:
            if c not in constraints:
                constraints.append(c)

        ctx_opts = extract_terms(context_text, OPTIONAL_CONTEXT_TERMS)
        for o in ctx_opts:
            if o not in optional_context:
                optional_context.append(o)

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


def normalize_optional_string(value: Any) -> str | None:
    text = " ".join(str(value or "").split())
    return text or None


def normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    cleaned: list[str] = []
    for item in value:
        text = " ".join(str(item or "").split())
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned


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
