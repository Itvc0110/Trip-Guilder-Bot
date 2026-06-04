from __future__ import annotations

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Ensure import paths work
sys.path.append(str(Path(__file__).parent))

from agent import DiChoiAgent, ConversationTurn
from config import load_settings


def print_separator(char="=", length=65):
    print(char * length)


def print_debug_trace(result, agent):
    print("\n" + "─" * 25 + " DEBUG TRACE " + "─" * 27)
    
    # 1. Routing & Decision
    route = result.route
    print(f"🔹 Routing Decision:  {route.get('decision', 'N/A').upper()}")
    print(f"🔹 Route Reason:      {route.get('reason', 'N/A')}")
    print(f"🔹 Missing Fields:    {route.get('missing_info', [])}")
    print(f"🔹 Tools Scheduled:   {route.get('tools_to_use', [])}")
    
    # 2. Extracted intent details from findings if available
    req_form = next((f.get("form") for f in result.tool_findings if f.get("tool_name") == "request_form"), None)
    if req_form:
        print("\n🔸 Extracted Intent:")
        print(f"  - Place Type:   {req_form.get('place_type')}")
        print(f"  - Location:     {req_form.get('location')}")
        print(f"  - Preferences:  {req_form.get('preferences')}")
        print(f"  - Constraints:  {req_form.get('constraints')}")
        print(f"  - Query Sent:   '{req_form.get('search_query')}'")
        
    # 3. Active plan state
    print("\n🔸 HangOut Plan:")
    if agent.hangout_plan:
        for idx, item in enumerate(agent.hangout_plan, 1):
            print(f"  {idx}. {item.get('title')} ({item.get('address', 'Chưa rõ địa chỉ')})")
    else:
        print("  (Kế hoạch trống)")
        
    print("─" * 65 + "\n")


def simulate_scenario():
    print_separator()
    print("MÔ PHỎNG KỊCH BẢN HỘI THOẠI ĐA LƯỢT (SCENARIO SIMULATION)")
    print_separator()
    
    settings = load_settings()
    # Unique ID for simulation so it doesn't conflict
    sim_id = "simulation_test_conversation"
    
    # Clean up old simulation conversation if exists
    sim_path = Path(__file__).parent / "conversations" / f"{sim_id}.json"
    if sim_path.exists():
        try:
            sim_path.unlink()
        except OSError:
            pass

    agent = DiChoiAgent(settings, conversation_id=sim_id)
    
    # The scenario turns:
    # 1. User says they want to go out in West Lake (No place type)
    # 2. Agent clarifies and asks for type. User says they want cafe and checkin (No location in this query!)
    # 3. User adds Santorini Vibes to plan
    turns = [
        "Tôi muốn đi chơi ở khu vực Tây Hồ.",
        "Tìm quán cafe chill view đẹp nhiều góc check-in.",
        "Thêm Santorini Vibes vào kế hoạch đi chơi."
    ]
    
    for idx, query in enumerate(turns, 1):
        print(f"\n[LƯỢT {idx}] User: '{query}'")
        result = agent.run(query)
        
        # If user asks to add to plan in turn 3, simulate click add to plan
        if idx == 3:
            # Let's find Santorini Vibes in recommendations or add it directly
            places = agent.last_recommendations
            target_place = next((p for p in places if "Santorini" in p.get("title", "")), None)
            if not target_place:
                target_place = {
                    "title": "Santorini Vibes",
                    "address": "181 P. Nhật Chiêu, Nhật Tân, Tây Hồ, Hà Nội",
                    "rating": 4.0,
                    "type": "Cà phê",
                    "gps": {"latitude": 21.0664, "longitude": 105.8192}
                }
            agent.add_to_plan(target_place)
            print("💾 (Simulated click: Added Santorini Vibes to HangOut Plan)")
            
        print(f"\nBot:\n{result.final_answer}")
        print_debug_trace(result, agent)
        print("-" * 65)

    print("\n✅ Hoàn thành mô phỏng kịch bản!")


def interactive_chat():
    print_separator()
    print("TRÒ CHUYỆN TƯƠNG TÁC KÈM TRACE DEBUG")
    print("Nhập 'exit' để thoát. Nhập 'plan' để xem hangout plan. Nhập 'reset' để xóa chat.")
    print_separator()
    
    settings = load_settings()
    agent = DiChoiAgent(settings, conversation_id="interactive_debug_session")
    
    while True:
        try:
            query = input("Bạn> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
            
        if not query:
            continue
            
        if query.lower() in {"exit", "quit"}:
            break
            
        if query.lower() == "reset":
            sim_path = agent.memory_path
            if sim_path.exists():
                sim_path.unlink()
            agent = DiChoiAgent(settings, conversation_id="interactive_debug_session")
            print("♻️ Đã reset hội thoại!")
            continue
            
        if query.lower() == "plan":
            print(f"\nHangOut Plan ({len(agent.hangout_plan)} điểm):")
            for idx, item in enumerate(agent.hangout_plan, 1):
                print(f"  {idx}. {item.get('title')} ({item.get('address')})")
            print()
            continue
            
        # Handle plan mutations triggers from query directly for CLI ease
        if query.lower().startswith("add "):
            place_name = query[4:].strip()
            agent.add_to_plan({
                "title": place_name,
                "address": "Chọn trực tiếp từ CLI test",
                "rating": "N/A",
                "type": "Tự chọn",
                "gps": None
            })
            print(f"➕ Đã thêm '{place_name}' vào Kế hoạch!")
            continue
            
        if query.lower().startswith("remove "):
            place_name = query[7:].strip()
            agent.remove_from_plan(place_name)
            print(f"➖ Đã xóa '{place_name}' khỏi Kế hoạch!")
            continue

        result = agent.run(query)
        print(f"\nBot>\n{result.final_answer}")
        print_debug_trace(result, agent)


def main():
    load_dotenv()
    print_separator()
    print("      DICHOIBOT CONVERSATION & MEMORY TESTING TOOL")
    print_separator()
    print("1. Chạy mô phỏng kịch bản (Scenario Simulation)")
    print("2. Chat tương tác kèm hiển thị Trace Log chi tiết")
    print_separator()
    
    try:
        choice = input("Lựa chọn của bạn (1-2): ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return
        
    if choice == "1":
        simulate_scenario()
    elif choice == "2":
        interactive_chat()
    else:
        print("Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()
