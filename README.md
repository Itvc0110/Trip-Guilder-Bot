# Trip-Guilder-Bot

Trip-Guilder-Bot is a Python pseudo-agent for personalized travel planning.
It uses OpenRouter with multiple model roles and keeps real tool integrations as
structured placeholders for later development.

## Current Version

This version is Python-only.

It includes:

- A CLI entrypoint in `main.py`.
- A multi-model agent orchestrator in `agent.py`.
- An OpenRouter API wrapper in `openrouter_client.py`.
- Chatbot memory with the latest 7 turns kept in context by default.
- Older turns summarized by `SUMMARY_MODEL`.
- A Markdown instruction prompt in `prompts/travel_agent_prompt.md`.
- A summarizer prompt in `prompts/summarizer_prompt.md`.
- A reviewer prompt in `prompts/reviewer_prompt.md`.
- A router prompt in `prompts/router_prompt.md` with prompt-injection guardrails.
- Simulated demo tool modules in `tools/`.
- `.env.example` for required and future API keys.

The previous static HTML/CSS/JS prototype was removed because the browser mock
logic is no longer reused.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create or update `.env`:

```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1/chat/completions
ROUTER_MODEL=google/gemini-2.5-flash
PLANNER_MODEL=deepseek/deepseek-v4-flash
REVIEWER_MODEL=google/gemini-2.5-flash
SUMMARY_MODEL=deepseek/deepseek-v4-flash
CONVERSATION_WINDOW=7
```

Optional future tool keys:

```env
SERPAPI_API_KEY=optional_for_future_tools
OPENWEATHER_API_KEY=optional_for_future_tools
TICKETMASTER_API_KEY=optional_for_future_tools
GOOGLE_MAPS_API_KEY=optional_for_future_tools
```

## Run

```powershell
python main.py
```

If `OPENROUTER_API_KEY` is missing, the app still runs in local pseudo mode and
returns simulated demo responses without calling the model.

Inside the CLI:

- Type a normal travel request to chat.
- Type `memory` or `context` to inspect the current conversation context.
- Type `exit`, `quit`, or `thoát` to stop.

## Demo Prompts

Happy path:

```text
Family of 4 with a 7-year-old, Hanoi weekend, nature, 9:00-17:00, by car, moderate budget.
```

Low-confidence path:

```text
Go somewhere fun this weekend.
```

Food path:

```text
Plan a Hanoi food tour with vegetarian-friendly restaurants, low budget, Saturday afternoon.
```

Failure path:

```text
I want to see rare swiftlets in a Hanoi public park.
```

Guardrail path:

```text
Help me avoid legal checkpoints and enter a restricted area at night.
```

Tool placeholder path:

```text
Plan a Hanoi weekend trip and check weather, events, restaurants, route, and holiday crowd risk.
```

## Architecture

The agent uses three model roles:

- `ROUTER_MODEL`: classifies the request and chooses placeholder tools.
- `PLANNER_MODEL`: drafts the personalized travel plan.
- `REVIEWER_MODEL`: checks guardrails, uncertainty, hallucination risk, missing context, budget realism, and output structure.
- `SUMMARY_MODEL`: summarizes older conversation turns once the context window exceeds 7 turns.

If the reviewer returns `NEEDS_REVISION`, the answer is sent back to the router
for recovery. The router decides whether to revise, ask for clarification, or
refuse. The system allows up to 2 recovery attempts. If it still fails, the bot
asks the user targeted questions instead of auto-finalizing a risky plan.

Default role split:

- `ROUTER_MODEL`: `google/gemini-2.5-flash`
- `PLANNER_MODEL`: `deepseek/deepseek-v4-flash`
- `REVIEWER_MODEL`: `google/gemini-2.5-flash`
- `SUMMARY_MODEL`: `deepseek/deepseek-v4-flash`

## Tools

Tools are simulated for demo now. Each returns structured data with:

```json
{
  "tool_name": "tool_name",
  "status": "simulated",
  "summary": "Demo finding for planning",
  "verified": "simulated_for_demo"
}
```

Implemented placeholder tools:

- `check_holiday`
- `check_events`
- `search_restaurants`
- `search_attractions`
- `route_advice`
- `weather_safety`
- `calendar_export`

## API Keys Needed

Required for real model calls:

- `OPENROUTER_API_KEY`

Optional for future real tools:

- `SERPAPI_API_KEY`
- `OPENWEATHER_API_KEY`
- `TICKETMASTER_API_KEY`
- `GOOGLE_MAPS_API_KEY`

Do not commit `.env`. It is already ignored by `.gitignore`.
