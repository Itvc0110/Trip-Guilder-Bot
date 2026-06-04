from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config import Settings
from openrouter_client import OpenRouterClient, OpenRouterError
from tools.registry import run_placeholder_tools


PROMPTS_DIR = Path(__file__).parent / "prompts"


@dataclass
class ConversationTurn:
    user: str
    assistant: str


@dataclass
class AgentResult:
    route: dict[str, Any]
    tool_findings: list[dict[str, Any]]
    draft_answer: str
    review: str
    final_answer: str
    memory_summary: str


class TravelAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenRouterClient(settings)
        self.router_prompt = (PROMPTS_DIR / "router_prompt.md").read_text(encoding="utf-8")
        self.travel_prompt = (PROMPTS_DIR / "travel_agent_prompt.md").read_text(encoding="utf-8")
        self.reviewer_prompt = (PROMPTS_DIR / "reviewer_prompt.md").read_text(encoding="utf-8")
        self.summarizer_prompt = (PROMPTS_DIR / "summarizer_prompt.md").read_text(encoding="utf-8")
        self.memory_summary = ""
        self.history: list[ConversationTurn] = []

    def run(self, user_request: str) -> AgentResult:
        conversation_context = self._conversation_context()
        route = self._route_request(user_request, conversation_context)
        tool_findings = run_placeholder_tools(route, user_request)

        if route.get("decision") == "refuse":
            draft_answer = self._safe_refusal(user_request, route)
            review = "Từ chối bằng guardrail local. Không cần gọi reviewer model."
            final_answer = draft_answer
        else:
            draft_answer = self._plan_trip(user_request, route, tool_findings, conversation_context)
            review = self._review_answer(user_request, draft_answer, tool_findings, conversation_context)
            final_answer = self._apply_review(draft_answer, review)

        self._remember(user_request, final_answer)
        return AgentResult(route, tool_findings, draft_answer, review, final_answer, self.memory_summary)

    def _route_request(self, user_request: str, conversation_context: str) -> dict[str, Any]:
        fallback = local_route_request(user_request)
        if not self.settings.has_api_key:
            return fallback

        user = f"""
Hãy phân loại yêu cầu mới nhất và chọn các tool cần dùng.

Context hội thoại:
{conversation_context}

Yêu cầu mới nhất:
{user_request}

Trả về JSON với các trường:
- decision: "clarify" | "plan" | "refuse"
- reason: chuỗi ngắn bằng tiếng Việt
- missing_info: danh sách chuỗi bằng tiếng Việt
- tools_to_use: danh sách có thể gồm check_holiday, check_events, search_restaurants, search_attractions, route_advice, weather_safety, calendar_export
- safety_issue: chuỗi hoặc null
"""
        try:
            content = self.client.chat(
                model=self.settings.router_model,
                messages=[
                    {"role": "system", "content": self.router_prompt},
                    {"role": "user", "content": user},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            parsed = json.loads(content)
            return normalize_route(parsed, fallback)
        except (OpenRouterError, json.JSONDecodeError):
            return fallback

    def _plan_trip(
        self,
        user_request: str,
        route: dict[str, Any],
        tool_findings: list[dict[str, Any]],
        conversation_context: str,
    ) -> str:
        if not self.settings.has_api_key:
            return local_demo_answer(user_request, route, tool_findings, conversation_context)

        messages = [
            {"role": "system", "content": self.travel_prompt},
            {
                "role": "user",
                "content": (
                    f"Context hội thoại:\n{conversation_context}\n\n"
                    f"Yêu cầu mới nhất:\n{user_request}\n\n"
                    f"Quyết định router:\n{json.dumps(route, indent=2, ensure_ascii=False)}\n\n"
                    f"Kết quả tool demo:\n{json.dumps(tool_findings, indent=2, ensure_ascii=False)}"
                ),
            },
        ]
        try:
            return self.client.chat(
                model=self.settings.planner_model,
                messages=messages,
                temperature=0.2,
            )
        except OpenRouterError as exc:
            return (
                "## Tóm Tắt Yêu Cầu Chuyến Đi\n"
                "Không thể gọi planning model.\n\n"
                "## Kết Quả Từ Công Cụ\n"
                f"- Trạng thái API: {exc}\n\n"
                "## Câu Hỏi Theo Dõi\n"
                "- Vui lòng kiểm tra OpenRouter API key rồi thử lại."
            )

    def _review_answer(
        self,
        user_request: str,
        draft_answer: str,
        tool_findings: list[dict[str, Any]],
        conversation_context: str,
    ) -> str:
        if not self.settings.has_api_key:
            return "Review pseudo local: dữ liệu tool đang là mô phỏng demo, cần xác minh khi nối API thật."

        try:
            return self.client.chat(
                model=self.settings.reviewer_model,
                messages=[
                    {"role": "system", "content": self.reviewer_prompt},
                    {
                        "role": "user",
                        "content": (
                            f"Context hội thoại:\n{conversation_context}\n\n"
                            f"Yêu cầu mới nhất:\n{user_request}\n\n"
                            f"Kết quả tool:\n{json.dumps(tool_findings, indent=2, ensure_ascii=False)}\n\n"
                            f"Câu trả lời nháp:\n{draft_answer}"
                        ),
                    },
                ],
                temperature=0.1,
            )
        except OpenRouterError as exc:
            return f"Reviewer model không khả dụng: {exc}"

    def _apply_review(self, draft_answer: str, review: str) -> str:
        return (
            f"{draft_answer.rstrip()}\n\n"
            "## Kiểm Tra Của Reviewer\n"
            f"{review.strip()}\n"
        )

    def _safe_refusal(self, user_request: str, route: dict[str, Any]) -> str:
        return (
            "## Tóm Tắt Yêu Cầu Chuyến Đi\n"
            f"Yêu cầu có nội dung không an toàn hoặc ngoài phạm vi: {user_request}\n\n"
            "## Phản Hồi An Toàn\n"
            "Mình không thể hỗ trợ hành vi du lịch bất hợp pháp, đi vào khu vực hạn chế "
            "hoặc né tránh kiểm tra an toàn. Mình có thể giúp lập tuyến đi hợp pháp, "
            "khung giờ an toàn hơn hoặc phương án công cộng thay thế.\n\n"
            "## Câu Hỏi Theo Dõi\n"
            "- Bạn muốn mình lập kế hoạch quanh điểm đến công cộng và khung giờ hợp pháp nào?\n\n"
            "## Kiểm Tra Của Reviewer\n"
            f"Guardrail local đã kích hoạt: {route.get('safety_issue') or route.get('reason')}\n"
        )

    def _conversation_context(self) -> str:
        parts = []
        if self.memory_summary:
            parts.append(f"Tóm tắt các lượt cũ hơn:\n{self.memory_summary}")
        if self.history:
            recent = []
            for index, turn in enumerate(self.history[-self.settings.conversation_window :], start=1):
                recent.append(
                    f"Lượt {index}\nUser: {turn.user}\nAssistant: {compact_text(turn.assistant, 900)}"
                )
            parts.append("Các lượt gần nhất:\n" + "\n\n".join(recent))
        return "\n\n".join(parts) if parts else "Chưa có context hội thoại trước đó."

    def _remember(self, user_request: str, assistant_answer: str) -> None:
        self.history.append(ConversationTurn(user=user_request, assistant=assistant_answer))
        if len(self.history) <= self.settings.conversation_window:
            return

        old_turns = self.history[: -self.settings.conversation_window]
        self.history = self.history[-self.settings.conversation_window :]
        self.memory_summary = self._summarize_old_turns(old_turns)

    def _summarize_old_turns(self, old_turns: list[ConversationTurn]) -> str:
        transcript = "\n\n".join(
            f"User: {turn.user}\nAssistant: {compact_text(turn.assistant, 1200)}" for turn in old_turns
        )
        previous_summary = self.memory_summary or "Chưa có tóm tắt trước đó."

        if not self.settings.has_api_key:
            return local_summarize(previous_summary, old_turns)

        try:
            return self.client.chat(
                model=self.settings.summary_model,
                messages=[
                    {"role": "system", "content": self.summarizer_prompt},
                    {
                        "role": "user",
                        "content": (
                            f"Tóm tắt hiện tại:\n{previous_summary}\n\n"
                            f"Các lượt cần nén:\n{transcript}"
                        ),
                    },
                ],
                temperature=0.1,
            )
        except OpenRouterError:
            return local_summarize(previous_summary, old_turns)


def local_route_request(user_request: str) -> dict[str, Any]:
    text = user_request.lower()
    unsafe_terms = [
        "avoid checkpoint",
        "avoid legal checkpoint",
        "bypass police",
        "restricted area",
        "trespass",
        "sneak into",
        "illegal",
        "né chốt",
        "tránh chốt",
        "vào khu cấm",
        "khu vực hạn chế",
        "đột nhập",
        "trái phép",
        "bất hợp pháp",
    ]
    if any(term in text for term in unsafe_terms):
        return {
            "decision": "refuse",
            "reason": "Yêu cầu du lịch không an toàn hoặc bất hợp pháp.",
            "missing_info": [],
            "tools_to_use": [],
            "safety_issue": "unsafe_or_illegal_travel",
        }

    missing_info = []
    if not any(term in text for term in ["hanoi", "ha noi", "hà nội", "hn", "destination", "city", "thành phố"]):
        missing_info.append("điểm đến hoặc điểm xuất phát")
    if not any(term in text for term in ["weekend", "cuối tuần", "saturday", "thứ bảy", "sunday", "chủ nhật", "date", "ngày", "tomorrow", "ngày mai"]):
        missing_info.append("ngày đi hoặc khung thời gian")
    if not any(term in text for term in ["food", "ăn", "ẩm thực", "nhà hàng", "sightseeing", "tham quan", "nature", "thiên nhiên", "công viên", "culture", "văn hóa", "relax", "nghỉ", "thư giãn", "event", "sự kiện"]):
        missing_info.append("mục đích chuyến đi hoặc sở thích chính")

    tools = ["check_holiday", "check_events", "route_advice", "weather_safety"]
    if any(term in text for term in ["food", "ăn", "ẩm thực", "restaurant", "nhà hàng", "vegetarian", "chay", "cafe", "cà phê"]):
        tools.append("search_restaurants")
    if any(term in text for term in ["sightseeing", "tham quan", "nature", "thiên nhiên", "culture", "văn hóa", "park", "công viên", "museum", "bảo tàng"]):
        tools.append("search_attractions")
    tools.append("calendar_export")

    return {
        "decision": "clarify" if len(missing_info) >= 2 else "plan",
        "reason": "Dùng router local vì API routing không khả dụng hoặc chưa cần gọi.",
        "missing_info": missing_info,
        "tools_to_use": tools,
        "safety_issue": None,
    }


def normalize_route(parsed: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    decision = parsed.get("decision")
    if decision not in {"clarify", "plan", "refuse"}:
        decision = fallback["decision"]
    tools = parsed.get("tools_to_use")
    if not isinstance(tools, list):
        tools = fallback["tools_to_use"]
    return {
        "decision": decision,
        "reason": str(parsed.get("reason") or fallback["reason"]),
        "missing_info": parsed.get("missing_info") if isinstance(parsed.get("missing_info"), list) else fallback["missing_info"],
        "tools_to_use": [str(tool) for tool in tools],
        "safety_issue": parsed.get("safety_issue") or fallback.get("safety_issue"),
    }


def local_demo_answer(
    user_request: str,
    route: dict[str, Any],
    tool_findings: list[dict[str, Any]],
    conversation_context: str,
) -> str:
    missing = route.get("missing_info", [])
    findings = "\n".join(
        f"- {item['tool_name']}: {item['summary']} ({item['status']})" for item in tool_findings
    )
    questions = "\n".join(f"- Bạn có thể cho biết {item} không?" for item in missing) or "- Bạn muốn phiên bản chậm hơn, tiết kiệm hơn hay tập trung vào ăn uống hơn?"
    return (
        "## Tóm Tắt Yêu Cầu Chuyến Đi\n"
        f"{user_request}\n\n"
        "## Bối Cảnh Đã Xác Nhận\n"
        "- Chatbot đã nhận yêu cầu và định tuyến bằng router local.\n"
        f"- Context hội thoại đang dùng: {compact_text(conversation_context, 260)}\n\n"
        "## Giả Định Hoặc Thông Tin Còn Thiếu\n"
        + ("\n".join(f"- Thiếu: {item}" for item in missing) if missing else "- Đủ bối cảnh để tạo bản nháp đầu tiên.")
        + "\n\n"
        "## Kết Quả Từ Công Cụ\n"
        f"{findings}\n\n"
        "## Gợi Ý Cá Nhân Hóa\n"
        "- Đây là bản demo giả lập như tool đã hoàn thiện, nhưng kết quả vẫn được đánh dấu `simulated` để không nhầm với dữ liệu live.\n"
        "- Kết hợp event + route để tránh khu đông/tắc, weather + attraction để chọn indoor/outdoor, restaurant + route để chọn điểm ăn thuận tuyến.\n\n"
        "## Lịch Trình Hoặc Tuyến Đường\n"
        "- Buổi sáng: chọn điểm ưu tiên cao nhất, tránh khung giờ đông nếu tool event/holiday cảnh báo.\n"
        "- Giữa ngày: chừa buffer nghỉ ngơi hoặc ăn trưa, ưu tiên nhà hàng thuận tuyến.\n"
        "- Buổi chiều: thêm một điểm gần đó, rồi để một slot tùy chọn để không quá tải.\n\n"
        "## Cảnh Báo\n"
        "- Dữ liệu hiện là simulated tool output cho prototype; khi nối API thật cần xác minh lại giờ mở cửa, thời tiết, sự kiện, giao thông và độ đông.\n\n"
        "## Câu Hỏi Theo Dõi\n"
        f"{questions}\n\n"
        "## Đề Xuất Tinh Chỉnh\n"
        "Bạn có thể tiếp tục nhắn trong cùng cuộc hội thoại; chatbot sẽ dùng 7 lượt gần nhất và tóm tắt các lượt cũ hơn."
    )


def local_summarize(previous_summary: str, old_turns: list[ConversationTurn]) -> str:
    bullets = [previous_summary] if previous_summary and previous_summary != "Chưa có tóm tắt trước đó." else []
    for turn in old_turns:
        bullets.append(f"- User từng yêu cầu: {compact_text(turn.user, 180)}")
    return "\n".join(bullets[-12:])


def compact_text(text: str, limit: int) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."
