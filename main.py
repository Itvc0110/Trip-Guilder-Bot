from __future__ import annotations

from agent import TravelAgent
from config import load_settings


def main() -> None:
    settings = load_settings()
    agent = TravelAgent(settings)

    print("Trip-Guilder-Bot - chatbot Python")
    print("Nhập yêu cầu chuyến đi, hoặc nhập 'exit' để thoát.")
    print(f"Context window: giữ {settings.conversation_window} lượt gần nhất.")
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
        if not user_request:
            print("Vui lòng nhập yêu cầu chuyến đi.")
            continue

        result = agent.run(user_request)
        print()
        print(f"Bot>\n{result.final_answer}")
        print()


if __name__ == "__main__":
    main()
