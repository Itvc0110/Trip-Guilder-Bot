import os
import json
import datetime
import uuid
from pathlib import Path
import pandas as pd
import streamlit as st

# Import project files
from config import load_settings
from agent import DiChoiAgent, ConversationTurn, CONVERSATIONS_DIR

# Set Page Config
st.set_page_config(
    page_title="DiChoiBot - AI Friend Hangout Planner",
    page_icon="🗺️",
    layout="wide"
)

# Custom premium styling
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    .recommendation-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .review-box {
        background-color: #f9f9f9;
        padding: 8px;
        border-radius: 5px;
        margin-top: 5px;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "settings" not in st.session_state:
    st.session_state.settings = load_settings()

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "agent" not in st.session_state:
    st.session_state.agent = DiChoiAgent(st.session_state.settings, st.session_state.conversation_id)
    st.session_state.conversation_id = st.session_state.agent.conversation_id

def submit_user_message(query_text: str):
    if query_text and query_text.strip():
        st.session_state.agent.run(query_text)
        st.rerun()

# Sidebar panel
with st.sidebar:
    st.title("🗺️ HangOut Control")
    st.write("---")

    # Load/Resume Conversation
    st.subheader("Hội thoại")
    CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)
    saved_files = sorted(CONVERSATIONS_DIR.glob("*.json"), reverse=True)
    file_options = ["Bắt đầu mới"] + [f.stem for f in saved_files]
    
    selected_option = st.selectbox(
        "Chọn hội thoại cũ:",
        options=file_options,
        index=0 if st.session_state.conversation_id not in [f.stem for f in saved_files] else file_options.index(st.session_state.conversation_id)
    )

    if selected_option == "Bắt đầu mới" and st.session_state.conversation_id is not None:
        if st.button("Tạo hội thoại mới"):
            st.session_state.conversation_id = None
            st.session_state.agent = DiChoiAgent(st.session_state.settings, None)
            st.session_state.conversation_id = st.session_state.agent.conversation_id
            st.rerun()
    elif selected_option != "Bắt đầu mới" and selected_option != st.session_state.conversation_id:
        st.session_state.conversation_id = selected_option
        st.session_state.agent = DiChoiAgent(st.session_state.settings, selected_option)
        st.rerun()

    st.write("---")
    st.subheader("⚙️ Cấu hình hiển thị")
    show_map = st.checkbox("🗺️ Bật Bản đồ & Tương tác", value=True)
    st.write("---")

    # HangOut Plan Framework Tracker
    st.subheader("📋 HangOut Plan Framework")
    st.info("AI trích xuất tự động từ ý định trò chuyện:")
    
    # We render fields that are extracted
    group_size = st.number_input("Số lượng bạn bè:", min_value=1, max_value=30, value=4)
    vibe = st.text_input("Vibe / Chủ đề đi chơi:", value="Ăn uống & Cafe chill")
    area = st.text_input("Khu vực cụ thể:", value="Tây Hồ, Hà Nội")
    timing = st.text_input("Thời gian:", value="Chiều tối thứ Bảy")

    st.write("---")

    # Current HangOut Plan Items
    st.subheader("📍 HangOut Plan")
    plan = st.session_state.agent.hangout_plan
    
    if not plan:
        st.warning("Kế hoạch trống. Hãy thêm các địa điểm đề xuất từ chat.")
    else:
        for idx, item in enumerate(plan):
            with st.expander(f"{idx+1}. {item.get('title')}", expanded=True):
                st.write(f"**Loại:** {item.get('type') or 'N/A'}")
                st.write(f"**Địa chỉ:** {item.get('address') or 'N/A'}")
                st.write(f"**Rating:** ⭐ {item.get('rating') or 'N/A'}")
                # Render delete button
                if st.button("Xóa khỏi kế hoạch", key=f"del_{idx}"):
                    st.session_state.agent.remove_from_plan(item.get("title"))
                    st.rerun()

        # ICS Export option
        st.write("---")
        st.subheader("📅 Export")
        
        # Build ics string
        ics_content = []
        ics_content.append("BEGIN:VCALENDAR")
        ics_content.append("VERSION:2.0")
        ics_content.append("PRODID:-//Trip-Guilder-Bot//NONSGML Itinerary//EN")
        ics_content.append("CALSCALE:GREGORIAN")
        ics_content.append("METHOD:PUBLISH")
        
        today = datetime.date.today()
        date_str = today.strftime("%Y%m%d")
        
        for idx, item in enumerate(plan):
            time_slot = f"{14 + idx*2:02d}:00 - {16 + idx*2:02d}:00"
            sh, sm = f"{14 + idx*2:02d}", "00"
            eh, em = f"{16 + idx*2:02d}", "00"
            dtstart = f"{date_str}T{sh}{sm}00"
            dtend = f"{date_str}T{eh}{em}00"
            
            uid = f"event-{idx}-{datetime.datetime.now().timestamp()}@tripguilderbot.local"
            dtstamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            
            ics_content.append("BEGIN:VEVENT")
            ics_content.append(f"UID:{uid}")
            ics_content.append(f"DTSTAMP:{dtstamp}")
            ics_content.append(f"DTSTART;TZID=Asia/Ho_Chi_Minh:{dtstart}")
            ics_content.append(f"DTEND;TZID=Asia/Ho_Chi_Minh:{dtend}")
            ics_content.append(f"SUMMARY:{item.get('title')}")
            ics_content.append(f"DESCRIPTION:Địa điểm trong kế hoạch HangOut")
            ics_content.append(f"LOCATION:{item.get('address', '')}")
            ics_content.append("END:VEVENT")
            
        ics_content.append("END:VCALENDAR")
        full_ics = "\r\n".join(ics_content)
        
        st.download_button(
            label="Tải lịch trình (.ics)",
            data=full_ics,
            file_name=f"hangout_plan_{date_str}.ics",
            mime="text/calendar"
        )

# Main Workspace
st.title("🗺️ DiChoiBot - AI Friend Hangout Planner")
st.write("Lên kế hoạch đi chơi cùng nhóm bạn dựa trên đánh giá thực tế của Google Maps.")

# Active flow steps visualization
st.write("**Quy trình lập kế hoạch:**")
cols = st.columns(4)
with cols[0]:
    st.success("1. Trích xuất ý định")
with cols[1]:
    st.info("2. Tìm & Phân tích Reviews")
with cols[2]:
    st.warning("3. Chọn & Thêm địa điểm")
with cols[3]:
    st.error("4. Xuất lịch trình đi chơi")

st.write("---")

# Split workspace layout into Left (Google Map & Actions) and Right (Chatbot) based on show_map toggle
if show_map:
    col_left, col_right = st.columns([4, 5])
else:
    col_left = None
    col_right = st.container()

# LEFT COLUMN: Google Map Panel & Location Interactions
if col_left:
    with col_left:
        st.subheader("🗺️ Bản đồ & Tương tác vị trí")
        
        # Compile options for map center selection
        map_options = ["Mặc định (Hà Nội)"]
        if area:
            map_options[0] = f"Mặc định ({area})"
            
        for item in plan:
            map_options.append(f"Plan: {item.get('title')} ({item.get('address')})")
            
        for item in agent.last_recommendations[:5]:
            map_options.append(f"Đề xuất: {item.get('title')} ({item.get('address')})")
            
        selected_map_opt = st.selectbox(
            "Chọn địa điểm để xem trên bản đồ:",
            options=map_options,
            index=0,
            key="map_center_selectbox"
        )
        
        # Parse selected address/query
        if selected_map_opt.startswith("Mặc định"):
            default_q = area if area else "Hà Nội"
            map_query = default_q
        elif selected_map_opt.startswith("Plan: "):
            map_query = selected_map_opt[len("Plan: "):].split(" (")[0]
        elif selected_map_opt.startswith("Đề xuất: "):
            map_query = selected_map_opt[len("Đề xuất: "):].split(" (")[0]
        else:
            map_query = selected_map_opt
            
        # Input box to customize or refine search on map
        map_search = st.text_input(
            "Tìm kiếm / Tinh chỉnh vị trí trên bản đồ:",
            value=map_query,
            key="map_search_input"
        )
        
        # Embed the Google Map iframe
        import urllib.parse
        encoded_search = urllib.parse.quote(map_search)
        embed_url = f"https://maps.google.com/maps?q={encoded_search}&t=&z=15&ie=UTF8&iwloc=&output=embed"
        
        st.components.v1.iframe(embed_url, height=450)
        
        # Map actions triggers
        st.markdown("##### ⚡ Tương tác vị trí với Chatbot:")
        st.write("Yêu cầu chatbot thực hiện tác vụ liên quan đến vị trí trên bản đồ:")
        
        col_act1, col_act2, col_act3 = st.columns(3)
        with col_act1:
            if st.button("🔍 Đánh giá", use_container_width=True, key="btn_review_map"):
                submit_user_message(f"Đọc review và đánh giá chi tiết quán: {map_search}")
        with col_act2:
            if st.button("📍 Xung quanh", use_container_width=True, key="btn_around_map"):
                submit_user_message(f"Gợi ý các địa điểm ăn uống, cafe hoặc vui chơi xung quanh: {map_search}")
        with col_act3:
            if st.button("➕ Thêm vào Plan", use_container_width=True, key="btn_add_direct_map"):
                agent.add_to_plan({
                    "title": map_search,
                    "address": "Địa điểm tự chọn từ bản đồ",
                    "rating": "N/A",
                    "type": "Tự chọn",
                    "gps": None
                })
                st.success(f"Đã thêm {map_search} vào kế hoạch!")
                st.rerun()
                
        st.write("---")
        
        # Show active plan route map at the bottom of the left column
        if plan:
            st.subheader("📍 Lộ trình các điểm đã chọn:")
            map_data = []
            for loc in plan:
                gps = loc.get("gps")
                if gps and isinstance(gps, dict):
                    lat = gps.get("latitude") or gps.get("lat")
                    lon = gps.get("longitude") or gps.get("lng")
                    if lat and lon:
                        map_data.append({
                            "latitude": float(lat),
                            "longitude": float(lon),
                            "title": loc.get("title")
                        })
                        
            if map_data:
                df = pd.DataFrame(map_data)
                st.map(df)
            else:
                st.info("Chưa có tọa độ GPS để hiển thị lộ trình.")

# RIGHT COLUMN: Chatbot Conversation & Recommendations
with col_right:
    # Render conversation turns
    for turn in agent.transcript:
        with st.chat_message("user"):
            st.write(turn.user)
        with st.chat_message("assistant"):
            st.write(turn.assistant)
            
    # Toggle flow choice "Bạn muốn đi tiếp không?"
    go_next = st.checkbox("Bạn muốn tiếp tục tìm và thêm địa điểm khác cho kế hoạch đi chơi không?", value=True)
    
    # Quick Reply Panel if Agent needs clarification
    if go_next and agent.last_route and agent.last_route.get("decision") == "clarify":
        missing_info = agent.last_route.get("missing_info", [])
        if missing_info:
            primary_missing = missing_info[0]
            
            # Map missing info to user options
            if "khu vực" in primary_missing.lower() or "thành phố" in primary_missing.lower() or "ở đâu" in primary_missing.lower():
                title = "Chọn khu vực bạn muốn đi chơi:"
                options = ["Tây Hồ, Hà Nội", "Hoàn Kiếm, Hà Nội", "Cầu Giấy, Hà Nội"]
            elif "trải nghiệm" in primary_missing.lower() or "kiểu" in primary_missing.lower():
                title = "Chọn kiểu trải nghiệm bạn muốn:"
                options = ["Cafe chill & sống ảo", "Ăn uống ẩm thực", "Vui chơi & hoạt động nhóm"]
            else:
                title = f"Vui lòng chọn một lựa chọn nhanh hoặc nhập tự chọn ở khung chat:"
                options = ["Tây Hồ, Hà Nội", "Cafe & Ăn uống", "Hoạt động ngoài trời"]
                
            st.markdown(f"""
            <div style="background-color: #f0f4f8; padding: 15px; border-radius: 8px; border-left: 5px solid #2b5c8f; margin-bottom: 15px;">
                <p style="margin: 0; font-weight: bold; color: #2b5c8f;">💡 Trả lời nhanh cho Bot:</p>
                <p style="margin: 5px 0 10px 0; font-size: 0.95em;">Bot đang thiếu thông tin: <b>{primary_missing}</b></p>
            </div>
            """, unsafe_allow_html=True)
            st.write(f"*{title}*")
            
            cols = st.columns(3)
            for idx, opt in enumerate(options):
                with cols[idx]:
                    if st.button(opt, key=f"quick_reply_{idx}", use_container_width=True):
                        submit_user_message(opt)
            st.write("---")
            
    # Main chat input block
    if go_next:
        user_query = st.chat_input("Nhập yêu cầu tìm quán cafe, chỗ ăn uống hay vui chơi, hoặc nhập câu trả lời của bạn...")
        if user_query:
            submit_user_message(user_query)
    else:
        st.success("🎉 Bạn đã quyết định chốt lịch trình này! Hãy tải lịch (.ics) từ sidebar hoặc xem sơ đồ bên dưới.")
        
    # Display recommended locations as interactive cards (if any are available)
    if agent.last_recommendations and go_next:
        st.subheader("📍 Địa điểm được đề xuất dựa trên đánh giá:")
        
        for idx, place in enumerate(agent.last_recommendations[:5]):
            with st.container():
                st.markdown(f"""
                <div class="recommendation-card">
                    <h3>{idx+1}. {place.get('title')} ({place.get('type') or 'Địa điểm'})</h3>
                    <p><b>Địa chỉ:</b> {place.get('address')}</p>
                    <p><b>Rating:</b> ⭐ {place.get('rating')} | <b>Score:</b> {place.get('score')} | <b>Giá:</b> {place.get('price') or 'Chưa rõ'}</p>
                    <p><i>{place.get('general_comment') or ''}</i></p>
                </div>
                """, unsafe_allowed_html=True)
                
                # Action button to add to plan
                if st.button(f"Thêm {place.get('title')} vào Kế hoạch", key=f"add_{idx}"):
                    agent.add_to_plan({
                        "title": place.get("title"),
                        "address": place.get("address"),
                        "rating": place.get("rating"),
                        "type": place.get("type"),
                        "gps": place.get("gps"),
                        "data_id": place.get("data_id")
                    })
                    st.success(f"Đã thêm {place.get('title')}!")
                    st.rerun()
