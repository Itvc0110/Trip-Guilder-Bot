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
- A Markdown instruction prompt in `prompts/travel_agent_prompt.md`.
- A reviewer prompt in `prompts/reviewer_prompt.md`.
- Placeholder tool modules in `tools/`.
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
PLANNER_MODEL=google/gemini-2.5-flash
REVIEWER_MODEL=google/gemini-2.5-flash
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
returns placeholder responses without calling the model.

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

All roles default to:

```text
google/gemini-2.5-flash
```

## Tools

Tools are placeholders for now. Each returns structured data with:

```json
{
  "tool_name": "tool_name",
  "status": "placeholder",
  "summary": "What this future tool will verify",
  "verified": false
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
