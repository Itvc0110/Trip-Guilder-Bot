from __future__ import annotations

from agent import TravelAgent
from config import load_settings


def main() -> None:
    settings = load_settings()
    agent = TravelAgent(settings)

    print("Trip-Guilder-Bot - pseudo-agent Python")
    print("Nhập yêu cầu chuyến đi, hoặc nhập 'exit' để thoát.")
    if not settings.has_api_key:
        print("Chưa có OPENROUTER_API_KEY; đang chạy chế độ pseudo local.")
    print()

    while True:
        try:
            user_request = input("Trip request> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_request.lower() in {"exit", "quit"}:
            break
        if not user_request:
            print("Vui lòng nhập yêu cầu chuyến đi.")
            continue

        result = agent.run(user_request)
        print()
        print(result.final_answer)
        print()


if __name__ == "__main__":
    main()
