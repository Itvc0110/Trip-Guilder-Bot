from __future__ import annotations

import atexit
import datetime as dt
import html
import json
import urllib.parse
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from agent import DiChoiAgent
from config import load_settings


SESSION_FILES: set[str] = set()


@atexit.register
def cleanup_session_files() -> None:
    """Delete only ephemeral Streamlit session files created by this process."""
    for file_name in list(SESSION_FILES):
        path = Path(file_name)
        try:
            if path.name.endswith("_session.json") and path.exists():
                path.unlink()
        except OSError:
            pass


st.set_page_config(
    page_title="DiChoiBot",
    page_icon="🧭",
    layout="wide",
)


st.markdown(
    """
    <style>
        .main .block-container { padding-top: 1.25rem; max-width: 1400px; }
        .small-muted { color: #667085; font-size: 0.9rem; }
        .recommendation-card {
            border: 1px solid #e4e7ec;
            border-radius: 8px;
            padding: 14px 16px;
            margin: 10px 0;
            background: #ffffff;
        }
        .recommendation-title {
            font-weight: 700;
            font-size: 1.05rem;
            margin-bottom: 4px;
        }
        .metric-row {
            color: #475467;
            font-size: 0.92rem;
            margin: 2px 0 8px 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_session() -> None:
    if "settings" not in st.session_state:
        st.session_state.settings = load_settings()
    if "agent" not in st.session_state:
        st.session_state.agent = DiChoiAgent(st.session_state.settings)
        SESSION_FILES.add(str(st.session_state.agent.memory_path))
    if "last_result_json" not in st.session_state:
        st.session_state.last_result_json = None


def reset_session() -> None:
    if "agent" in st.session_state:
        st.session_state.agent.delete_session_memory()
    st.session_state.agent = DiChoiAgent(st.session_state.settings)
    SESSION_FILES.add(str(st.session_state.agent.memory_path))
    st.session_state.last_result_json = None
    st.rerun()


def submit_user_message(message: str) -> None:
    message = message.strip()
    if not message:
        return
    result = st.session_state.agent.run(message)
    st.session_state.last_result_json = result.response_json
    SESSION_FILES.add(str(st.session_state.agent.memory_path))
    st.rerun()


def safe_text(value: Any, fallback: str = "Chưa rõ") -> str:
    text = str(value or "").strip()
    return text if text else fallback


def escape_ics(value: Any) -> str:
    text = str(value or "")
    return (
        text.replace("\\", "\\\\")
        .replace(",", "\\,")
        .replace(";", "\\;")
        .replace("\n", "\\n")
        .replace("\r", "")
    )


def build_ics(plan: list[dict[str, Any]]) -> tuple[str, str]:
    today = dt.date.today()
    date_str = today.strftime("%Y%m%d")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//DiChoiBot//Hangout Plan//VI",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]
    for index, item in enumerate(plan):
        start_hour = min(22, 14 + index * 2)
        end_hour = min(23, start_hour + 2)
        uid = f"dichoibot-{index}-{dt.datetime.now().timestamp()}@local"
        dtstamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{dtstamp}",
                f"DTSTART;TZID=Asia/Ho_Chi_Minh:{date_str}T{start_hour:02d}0000",
                f"DTEND;TZID=Asia/Ho_Chi_Minh:{date_str}T{end_hour:02d}0000",
                f"SUMMARY:{escape_ics(item.get('title'))}",
                f"DESCRIPTION:{escape_ics(item.get('general_comment') or 'Địa điểm trong kế hoạch DiChoiBot')}",
                f"LOCATION:{escape_ics(item.get('address'))}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines), date_str


def add_to_plan(place: dict[str, Any]) -> None:
    st.session_state.agent.add_to_plan(
        {
            "title": place.get("title"),
            "address": place.get("address"),
            "rating": place.get("rating"),
            "type": place.get("type"),
            "gps": place.get("gps"),
            "data_id": place.get("data_id"),
            "price": place.get("price"),
            "score": place.get("score"),
            "general_comment": place.get("general_comment"),
        }
    )
    st.rerun()


def render_sidebar(agent: DiChoiAgent) -> bool:
    with st.sidebar:
        st.title("DiChoiBot")
        st.caption("Session memory chỉ dùng trong phiên hiện tại. App không tự load chat cũ từ local.")

        if st.button("Tạo phiên mới", use_container_width=True):
            reset_session()

        st.divider()
        st.subheader("Trạng thái")
        st.write(f"Memory file: `{agent.memory_path.name}`")
        st.write(f"Context window: `{agent.settings.conversation_window}` lượt")
        if agent.settings.has_api_key:
            st.success("OpenRouter API key đã sẵn sàng.")
        else:
            st.warning("Chưa có OPENROUTER_API_KEY, đang dùng pseudo local fallback.")

        show_map = st.toggle("Hiển thị bản đồ", value=True)
        show_debug = st.toggle("Hiển thị debug JSON", value=False)

        st.divider()
        st.subheader("Request state")
        st.json(agent.request_state, expanded=False)

        if show_debug:
            st.subheader("Tool log")
            if agent.tool_log:
                st.dataframe(agent.tool_log, use_container_width=True)
            else:
                st.info("Chưa có tool log trong phiên này.")

            st.subheader("Last JSON")
            st.json(st.session_state.last_result_json or {}, expanded=False)

        st.divider()
        st.subheader("Hangout plan")
        plan = agent.hangout_plan
        if not plan:
            st.info("Chưa có địa điểm nào trong plan.")
        else:
            for index, item in enumerate(plan):
                title = safe_text(item.get("title"), "Địa điểm")
                with st.expander(f"{index + 1}. {title}", expanded=False):
                    st.write(f"Địa chỉ: {safe_text(item.get('address'))}")
                    st.write(f"Rating: {safe_text(item.get('rating'))}")
                    st.write(f"Loại: {safe_text(item.get('type'))}")
                    if st.button("Xóa khỏi plan", key=f"delete_plan_{index}", use_container_width=True):
                        agent.remove_from_plan(title)
                        st.rerun()

            ics_content, date_str = build_ics(plan)
            st.download_button(
                "Tải lịch .ics",
                data=ics_content,
                file_name=f"dichoibot_plan_{date_str}.ics",
                mime="text/calendar",
                use_container_width=True,
            )

    return show_map


def render_map_panel(agent: DiChoiAgent) -> None:
    st.subheader("Bản đồ")

    map_options = []
    state_location = agent.request_state.get("location") or "Hà Nội"
    state_query = agent.request_state.get("search_query") or state_location
    map_options.append(("Nhu cầu hiện tại", state_query))

    for item in agent.hangout_plan:
        map_options.append((f"Plan: {safe_text(item.get('title'))}", item.get("address") or item.get("title")))

    for item in agent.last_recommendations[:5]:
        map_options.append((f"Đề xuất: {safe_text(item.get('title'))}", item.get("address") or item.get("title")))

    labels = [label for label, _ in map_options]
    selected_label = st.selectbox("Chọn điểm xem trên bản đồ", labels)
    selected_query = next(query for label, query in map_options if label == selected_label)
    map_search = st.text_input("Query bản đồ", value=safe_text(selected_query, "Hà Nội"))
    encoded_search = urllib.parse.quote(map_search)
    embed_url = f"https://maps.google.com/maps?q={encoded_search}&t=&z=15&ie=UTF8&iwloc=&output=embed"
    st.components.v1.iframe(embed_url, height=420)

    cols = st.columns(3)
    with cols[0]:
        if st.button("Đọc review điểm này", use_container_width=True):
            submit_user_message(f"Đọc review và đánh giá địa điểm: {map_search}")
    with cols[1]:
        if st.button("Tìm quanh đây", use_container_width=True):
            submit_user_message(f"Gợi ý chỗ đi chơi, ăn uống hoặc cafe quanh {map_search}")
    with cols[2]:
        if st.button("Thêm vào plan", use_container_width=True):
            agent.add_to_plan(
                {
                    "title": map_search,
                    "address": "Địa điểm chọn từ bản đồ",
                    "rating": "N/A",
                    "type": "Tự chọn",
                    "gps": None,
                }
            )
            st.rerun()

    gps_rows = []
    for item in agent.hangout_plan:
        gps = item.get("gps")
        if isinstance(gps, dict):
            lat = gps.get("latitude") or gps.get("lat")
            lon = gps.get("longitude") or gps.get("lng")
            if lat and lon:
                gps_rows.append({"latitude": float(lat), "longitude": float(lon)})
    if gps_rows:
        st.map(pd.DataFrame(gps_rows))


def render_chat(agent: DiChoiAgent) -> None:
    st.subheader("Chat")

    for turn in agent.transcript:
        with st.chat_message("user"):
            st.write(turn.user)
        with st.chat_message("assistant"):
            st.markdown(turn.assistant)

    questions = []
    if agent.last_response and isinstance(agent.last_response.get("follow_up_questions"), list):
        questions = agent.last_response["follow_up_questions"]
    if questions:
        st.info("Bot đang cần bạn bổ sung thông tin.")
        cols = st.columns(min(3, max(1, len(questions))))
        for index, question in enumerate(questions[:3]):
            with cols[index % len(cols)]:
                st.caption(question)

    st.markdown("#### Gợi ý nhanh")
    quick_prompts = [
        "Tìm quán cà phê yên tĩnh ở Hà Nội",
        "Mình muốn đi chơi gần VinUni",
        "Ưu tiên giá rẻ, dễ gửi xe",
    ]
    quick_cols = st.columns(3)
    for index, prompt in enumerate(quick_prompts):
        with quick_cols[index]:
            if st.button(prompt, key=f"quick_prompt_{index}", use_container_width=True):
                submit_user_message(prompt)

    user_query = st.chat_input("Nhập nhu cầu hoặc trả lời câu hỏi của bot...")
    if user_query:
        submit_user_message(user_query)


def render_recommendations(agent: DiChoiAgent) -> None:
    recommendations = agent.last_recommendations[:5]
    if not recommendations:
        return

    st.subheader("Địa điểm được đề xuất")
    for index, place in enumerate(recommendations):
        title = safe_text(place.get("title"), "Địa điểm chưa rõ tên")
        address = safe_text(place.get("address"))
        rating = safe_text(place.get("rating"))
        score = safe_text(place.get("score"))
        price = safe_text(place.get("price"))
        comment = safe_text(place.get("general_comment"), "")
        safe_comment = html.escape(comment)

        st.markdown(
            f"""
            <div class="recommendation-card">
                <div class="recommendation-title">{index + 1}. {html.escape(title)}</div>
                <div class="metric-row">Địa chỉ: {html.escape(address)}</div>
                <div class="metric-row">Rating: {html.escape(rating)} | Score: {html.escape(score)} | Giá: {html.escape(price)}</div>
                <div>{safe_comment}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        cols = st.columns([1, 3])
        with cols[0]:
            if st.button("Thêm vào plan", key=f"add_recommendation_{index}", use_container_width=True):
                add_to_plan(place)
        with cols[1]:
            if st.button("Hỏi kỹ hơn", key=f"ask_more_{index}", use_container_width=True):
                submit_user_message(f"Phân tích kỹ hơn địa điểm {title}, ưu nhược điểm theo review")


def main() -> None:
    init_session()
    agent: DiChoiAgent = st.session_state.agent
    show_map = render_sidebar(agent)

    st.title("DiChoiBot")
    st.caption("Tìm quán cafe, quán ăn, chỗ chill hoặc địa điểm đi chơi ngắn hạn dựa trên review.")

    if show_map:
        col_map, col_chat = st.columns([4, 5])
        with col_map:
            render_map_panel(agent)
        with col_chat:
            render_chat(agent)
            render_recommendations(agent)
    else:
        render_chat(agent)
        render_recommendations(agent)


if __name__ == "__main__":
    main()
