"""Optional LLM planning and grounded synthesis for OpsPilot investigations.

When OPENAI_API_KEY is absent or the provider call fails, the service safely
falls back to deterministic routing and synthesis. No infrastructure actions
are performed by this module.
"""
from __future__ import annotations

import json
import re
from typing import Any

from app.core.config import settings

ALLOWED_ROUTES = {"cloud", "knowledge", "incident"}


def _deterministic_routes(question: str) -> tuple[list[str], str]:
    text = question.lower()
    routes: list[str] = []
    cloud_terms = ("cost", "spend", "billing", "ec2", "aws", "gcp", "cloud", "cpu", "memory", "utilization", "resource", "instance", "infrastructure", "server")
    knowledge_terms = ("document", "runbook", "manual", "documentation", "recommend", "procedure", "how do i", "how should", "steps", "policy", "guide", "investigate", "root cause")
    incident_terms = ("incident", "outage", "error", "latency", "failure", "ticket", "alert", "production")
    if any(term in text for term in cloud_terms):
        routes.append("cloud")
    if any(term in text for term in knowledge_terms):
        routes.append("knowledge")
    if any(term in text for term in incident_terms):
        routes.append("incident")
    if not routes:
        routes = ["knowledge"]
    rationale = "Deterministic keyword-based routing was used because an LLM was not configured or available."
    return routes, rationale


def plan_investigation(question: str, api_key: str | None = None, model: str | None = None) -> dict[str, Any]:
    """Choose specialist routes using an optional LLM, with safe fallback."""
    key = settings.OPENAI_API_KEY if api_key is None else api_key
    selected_model = model or settings.OPENAI_MODEL
    if not key:
        routes, rationale = _deterministic_routes(question)
        return {"selected_routes": routes, "rationale": rationale,
                "reasoning_mode": "deterministic_fallback", "model": None}

    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        response = client.chat.completions.create(
            model=selected_model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": (
                    "You are the routing planner for OpsPilot AI. Choose which specialist agents are "
                    "needed for an operational investigation. Available agents: cloud (inventory, costs, "
                    "utilization), knowledge (indexed runbooks and documents), incident (open incidents). "
                    "Return JSON only with keys selected_routes (array containing only cloud, knowledge, "
                    "incident) and rationale (short string). Choose one or more agents. Never propose "
                    "infrastructure actions or claim to have inspected data."
                )},
                {"role": "user", "content": question},
            ],
        )
        content = response.choices[0].message.content or "{}"
        payload = json.loads(content)
        raw_routes = payload.get("selected_routes", [])
        routes = list(dict.fromkeys(route for route in raw_routes if route in ALLOWED_ROUTES))
        if not routes:
            raise ValueError("Planner returned no valid specialist routes")
        rationale = str(payload.get("rationale", "LLM selected specialist agents."))[:600]
        return {"selected_routes": routes, "rationale": rationale,
                "reasoning_mode": "llm", "model": selected_model}
    except Exception as exc:
        routes, _ = _deterministic_routes(question)
        return {"selected_routes": routes,
                "rationale": f"LLM planning unavailable ({type(exc).__name__}); deterministic routing was used.",
                "reasoning_mode": "deterministic_fallback", "model": None}


def synthesize_with_llm(question: str, findings: dict[str, Any], api_key: str | None = None,
                        model: str | None = None) -> dict[str, Any] | None:
    """Generate a grounded summary from collected evidence; return None on fallback."""
    key = settings.OPENAI_API_KEY if api_key is None else api_key
    selected_model = model or settings.OPENAI_MODEL
    if not key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        evidence = json.dumps(findings, default=str)[:18000]
        response = client.chat.completions.create(
            model=selected_model,
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": (
                    "You are OpsPilot AI's evidence-grounded operations analyst. Use ONLY the supplied "
                    "evidence. Do not invent metrics, incidents, asset identifiers, causes, or runbook "
                    "instructions. Clearly label hypotheses and missing evidence. Return JSON with "
                    "answer (string) and recommended_actions (array of strings). Recommendations must "
                    "be read-only investigative steps or approval-gated proposals. Never claim to execute "
                    "changes. Include source filenames/incident IDs when present."
                )},
                {"role": "user", "content": f"Question: {question}\nEvidence JSON: {evidence}"},
            ],
        )
        payload = json.loads(response.choices[0].message.content or "{}")
        answer = payload.get("answer")
        actions = payload.get("recommended_actions", [])
        if not isinstance(answer, str) or not answer.strip() or not isinstance(actions, list):
            return None
        return {"answer": answer[:12000],
                "recommended_actions": [str(x)[:500] for x in actions[:10]],
                "reasoning_mode": "llm", "model": selected_model}
    except Exception:
        return None
