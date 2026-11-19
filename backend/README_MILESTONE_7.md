# OpsPilot AI — Milestone 7: LLM-Powered Agent Reasoning

Milestone 7 adds optional LLM-based planning and evidence-grounded synthesis to the existing LangGraph workflow. It preserves demo mode and all Milestones 1–6 functionality.

## What's new

- Optional LLM planner chooses among the cloud, knowledge, and incident specialists.
- Planner output is constrained to an allowlist of known specialist routes.
- Specialist agents continue to collect evidence through the existing services.
- Optional LLM synthesis turns collected evidence into an investigation summary and recommended next steps.
- Prompts explicitly prohibit invented metrics, incidents, asset IDs, and claims that infrastructure actions were executed.
- A deterministic fallback is used when LLM mode is disabled, the API key is absent, or an LLM call fails.
- New response metadata: `reasoning_mode`, `selected_agents`, `planning_rationale`, and `model`.
- New status endpoint: `GET /api/v1/agents/reasoning/status`.

## Cost and safety

LLM mode is **opt-in**. The default is deterministic and makes no LLM API calls. To use LLM mode, you need an OpenAI API key and API billing; ChatGPT subscriptions do not include API usage. API usage may incur charges based on model and tokens. Do not enable LLM mode unless you understand and accept those costs.

No cloud account is required. The workflow continues to use the Milestone 6 demo data and the existing local RAG index. No infrastructure write operations are implemented. Human approval remains required for production changes.

## Enable deterministic mode (default)

In `backend/.env`:

```env
AGENT_REASONING_MODE=deterministic
OPENAI_API_KEY=
```

This mode uses constrained keyword routing and deterministic evidence synthesis.

## Opt in to LLM mode (optional)

In `backend/.env`:

```env
AGENT_REASONING_MODE=llm
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Keep the key local, never commit `.env`, and set a budget/usage alert in your API account. Restart FastAPI after changing environment variables.

Check configuration at `GET /api/v1/agents/reasoning/status`. The response never exposes the API key.

## API

The existing `POST /api/v1/agents/investigate` endpoint now includes planning metadata. Example request:

```json
{
  "question": "Our production EC2 instance has high CPU utilization. Check cloud metrics, investigate the runbook, and identify related incidents."
}
```

The response includes `selected_agents`, `planning_rationale`, `reasoning_mode`, and `model`. When LLM mode is disabled or fails, `reasoning_mode` reports `deterministic_fallback`.

## Run locally

Keep the existing Milestone 6 setup and `.env`/Qdrant data. Install requirements only if changed, then run MCP and FastAPI in separate terminals as before.

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

Milestone 6 had 25 tests. Milestone 7 adds five tests; expected total: 30.
