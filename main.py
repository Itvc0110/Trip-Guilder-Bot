from __future__ import annotations

import argparse
import json
from pathlib import Path

from agent import CONVERSATIONS_DIR, DiChoiAgent
from config import load_settings


def main() -> None:
    args = parse_args()
    if args.list_conversations:
        list_conversations()
        return

    settings = load_settings()
    agent = DiChoiAgent(settings, conversation_id=args.conversation)

    print("DiChoiBot - chatbot tìm chỗ đi chơi")
    print("Nhập nhu cầu tìm chỗ ăn, cafe, đi chơi ngắn hạn, hoặc nhập 'exit' để thoát.")
    print(f"Memory file: {agent.memory_path}")
    print(f"Context window: giữ {settings.conversation_window} lượt gần nhất.")
    print(f"Max reviewer recovery: 10 lần.")
    print(f"Model tóm tắt lượt cũ: {settings.summary_model}")
    if not settings.has_api_key:
        print("Chưa có OPENROUTER_API_KEY; đang chạy chế độ pseudo local.")
    print()

    while True:
        try:
            user_request = input("Bạn> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_request.lower() in {"exit", "quit", "thoát"}:
            break
        if user_request.lower() in {"memory", "context"}:
            print()
            print(agent._conversation_context())
            print()
            continue
        if user_request.lower() in {"memory_file", "file"}:
            print()
            print(agent.memory_path)
            print()
            continue
        if not user_request:
            print("Vui lòng nhập nhu cầu tìm chỗ đi chơi.")
            continue

        previous_memory_path = agent.memory_path
        result = agent.run(user_request)
        print()
        if agent.memory_path != previous_memory_path:
            print(f"Memory file: {agent.memory_path}")
        print(f"Bot>\n{result.final_answer}")
        print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DiChoiBot CLI")
    parser.add_argument(
        "--conversation",
        "-c",
        help="Tên file/id hội thoại để resume, ví dụ: 20260604-153000_cafe-tay-ho",
    )
    parser.add_argument(
        "--list-conversations",
        action="store_true",
        help="Liệt kê các file hội thoại đã lưu.",
    )
    return parser.parse_args()


def list_conversations() -> None:
    CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(CONVERSATIONS_DIR.glob("*.json"), reverse=True)
    if not files:
        print("Chưa có file hội thoại nào trong conversations/.")
        return

    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            print(f"- {path.name}")
            continue
        turns = data.get("transcript") or []
        updated = data.get("updated_at") or "unknown"
        first_user = ""
        if turns and isinstance(turns[0], dict):
            first_user = str(turns[0].get("user") or "")
        suffix = f" - {first_user[:80]}" if first_user else ""
        print(f"- {path.name} | updated: {updated} | turns: {len(turns)}{suffix}")


if __name__ == "__main__":
    main()
