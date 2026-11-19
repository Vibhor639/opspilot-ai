# OpsPilot AI architecture — Milestone 3

## RAG flow
1. API receives an allowed document upload.
2. Parser extracts text and page metadata.
3. Chunker creates overlapping word-window passages.
4. FastEmbed generates 384-dimensional vectors.
5. Qdrant stores vectors and source metadata on local disk.
6. Query is embedded and nearest-neighbor candidates are retrieved.
7. Lexical coverage is combined with vector similarity for a lightweight rerank.
8. The answer generator uses OpenAI when configured; otherwise it returns cited excerpts as an extractive fallback.

## Important engineering boundaries
- Retrieval and generation are separate modules.
- Uploaded text is treated as untrusted reference content.
- No tool execution or infrastructure changes are possible from retrieved documents.
- Current local Qdrant storage is for single-process development, not multi-worker production.
- OCR for scanned PDFs and neural cross-encoder reranking are future enhancements.


## Milestone 4 — Agent orchestration
- LangGraph `StateGraph` models the workflow.
- Supervisor routes questions to cloud, knowledge, and incident specialists.
- Specialist nodes call existing service modules rather than duplicating business logic.
- Synthesis combines findings and always marks operational changes as requiring human approval.
- Run history is process-local for development; production requires durable persistence and tenant isolation.
- No write-capable tools are exposed in this milestone.

## Milestone 6 — Live cloud provider boundary

`app/services/cloud_providers.py` isolates provider SDK calls from API and MCP layers. `CLOUD_MODE=demo` remains the default; `CLOUD_MODE=live` enables read-only provider requests. AWS uses the standard boto3 credential chain; GCP uses Application Default Credentials. No credentials are accepted through request payloads. Provider access is restricted to inventory, monitoring and billing reads. GCP billing depends on a configured BigQuery billing export. The Milestone 4 agent graph remains deterministic in this milestone; Milestone 7 will integrate live tools into agent reasoning.

## Milestone 7: optional LLM reasoning

The LangGraph supervisor can now receive specialist routes from an optional LLM planner. The planner is constrained to the existing cloud, knowledge, and incident specialist allowlist. The synthesis node can optionally use an LLM to summarize collected evidence. `AGENT_REASONING_MODE=deterministic` is the default and makes no LLM API calls; `AGENT_REASONING_MODE=llm` opts in when `OPENAI_API_KEY` is configured. If a provider call fails, the workflow falls back to deterministic planning/synthesis. Infrastructure actions remain outside the graph and human approval remains required.
