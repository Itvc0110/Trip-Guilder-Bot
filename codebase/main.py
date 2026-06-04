from __future__ import annotations

import json
import sys

from agent import DiChoiAgent
from config import load_settings


def main() -> None:
    configure_stdio()
    settings = load_settings()
    agent = DiChoiAgent(settings)

    print("DiChoiBot - chatbot tìm chỗ đi chơi")
    print("Nhập nhu cầu tìm chỗ ăn, cafe, đi chơi ngắn hạn, hoặc nhập 'exit' để thoát.")
    print(f"Session memory file: {agent.memory_path}")
    print(f"Context window: giữ {settings.conversation_window} lượt gần nhất trong phiên hiện tại.")
    print("Memory mode: ephemeral, xóa file session khi đóng chat.")
    print("Lệnh debug: context | state | tool_log | memory_file | last_json")
    print(f"Max reviewer recovery: 10 lần.")
    print(f"Model tóm tắt lượt cũ trong phiên: {settings.summary_model}")
    if not settings.has_api_key:
        print("Chưa có OPENROUTER_API_KEY; đang chạy chế độ pseudo local.")
    print()

    try:
        while True:
            try:
                user_request = input("Bạn> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            command = user_request.lower()
            if command in {"exit", "quit", "thoát", "thoat"}:
                break
            if command in {"memory", "context"}:
                print()
                print(agent._conversation_context())
                print()
                continue
            if command == "state":
                print()
                print(json.dumps(agent.request_state, ensure_ascii=False, indent=2))
                print()
                continue
            if command == "tool_log":
                print()
                print(json.dumps(agent.tool_log, ensure_ascii=False, indent=2))
                print()
                continue
            if command in {"memory_file", "file"}:
                print()
                print(agent.memory_path)
                print()
                continue
            if command == "last_json":
                print()
                print(json.dumps(agent.last_response or {}, ensure_ascii=False, indent=2))
                print()
                continue
            if not user_request:
                print("Vui lòng nhập nhu cầu tìm chỗ đi chơi.")
                continue

            result = agent.run(user_request)
            print()
            print(f"Bot>\n{result.final_answer}")
            print()
    finally:
        memory_path = agent.memory_path
        agent.delete_session_memory()
        if not memory_path.exists():
            print(f"Đã xóa session memory file: {memory_path}")


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


if __name__ == "__main__":
    main()
