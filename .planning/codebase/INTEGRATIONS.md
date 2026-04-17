# External Integrations

**Analysis Date:** 2026-04-17

## APIs & External Services

**LLM Providers:**

**OpenAI:**
- SDK: `openai>=1.91.0` (required)
- Models: GPT-5 family (gpt-5-mini, gpt-5-nano), GPT-4.1 family (gpt-4.1, gpt-4.1-mini, gpt-4.1-nano), legacy GPT-4o
- Auth: `OPENAI_API_KEY` environment variable
- Client: `AsyncOpenAI` (async HTTP client)
- Implementation: `graphiti_core/llm_client/openai_client.py`
- Features: Structured output via JSON mode, reasoning models (temperature=0 forced for reasoning models)

**Anthropic:**
- SDK: `anthropic>=0.49.0` (optional, `[anthropic]` extra)
- Models: Claude 4.5 (claude-sonnet-4-5-latest, claude-haiku-4-5-latest), Claude 3.7 (claude-3-7-sonnet), Claude 3.5 (claude-3-5-sonnet, claude-3-5-haiku), Claude 3 (opus, sonnet), Claude 2.x legacy
- Auth: `ANTHROPIC_API_KEY` environment variable (pulled from env if not in config)
- Client: `AsyncAnthropic`
- Implementation: `graphiti_core/llm_client/anthropic_client.py`
- Max tokens by model: 65536 (Claude 4.5, 3.7), 8192 (Claude 3.5, 3), 4096 (Claude 2)
- Features: Structured output support, async streaming

**Google Gemini:**
- SDK: `google-genai>=1.62.0` (optional, `[google-genai]` extra)
- Models: Gemini 3 (preview, gpt-3-flash-preview), Gemini 2.5 (pro, flash, flash-lite), Gemini 2.0, Gemini 1.5 (pro, flash)
- Auth: `GOOGLE_API_KEY` environment variable
- Client: `google.genai` (async-capable)
- Implementation: `graphiti_core/llm_client/gemini_client.py`
- Features: Structured JSON output with schema validation

**Groq:**
- SDK: `groq>=0.2.0` (optional, `[groq]` extra)
- Models: Fast inference provider (specific models documented in Groq SDK)
- Auth: `GROQ_API_KEY` environment variable
- Client: Groq AsyncClient
- Implementation: `graphiti_core/llm_client/groq_client.py`
- Features: High-speed LLM inference

**Azure OpenAI:**
- SDK: Part of `openai` package (AsyncAzureOpenAI)
- Auth: Azure service principal via azure-identity (optional, `[azure]` extra in MCP server)
- Implementation: `graphiti_core/llm_client/azure_openai_client.py` (server/)
- Features: Azure-managed OpenAI deployments with Azure AD authentication

## Embedding Providers

**OpenAI Embeddings:**
- SDK: `openai>=1.91.0` (required)
- Models: text-embedding-3-small (default), text-embedding-3-large
- Auth: `OPENAI_API_KEY`
- Client: `AsyncOpenAI.embeddings`
- Implementation: `graphiti_core/embedder/openai.py`
- Dimension: Configurable via `EMBEDDING_DIM` env var (default: 1024)

**Voyage AI Embeddings:**
- SDK: `voyageai>=0.2.3` (optional, `[voyageai]` extra)
- Models: voyage-3 (default)
- Auth: `VOYAGE_API_KEY` environment variable
- Client: `voyageai.AsyncClient`
- Implementation: `graphiti_core/embedder/voyage.py`
- Dimension: Configurable via `EMBEDDING_DIM` env var

**Sentence Transformers (Local):**
- SDK: `sentence-transformers>=3.2.1` (optional, `[sentence-transformers]` extra)
- Models: HuggingFace-compatible models for local embedding
- Auth: None (runs locally)
- Implementation: Local embedding execution in `graphiti_core/embedder/`
- Dimension: Model-dependent

**Gemini Embeddings:**
- SDK: `google-genai>=1.62.0` (via `[google-genai]` extra)
- Auth: `GOOGLE_API_KEY`
- Implementation: `graphiti_core/embedder/gemini.py`
- Features: Cloud-based embedding with Gemini models

## Data Storage

**Databases:**

**Neo4j:**
- Provider: Neo4j 5.26+ (required)
- Protocol: `bolt://` (binary protocol)
- Connection: `AsyncGraphDatabase.driver(uri, auth)`
- Async: Full async/await support
- Client: `neo4j` package (built-in dependency)
- Implementation: `graphiti_core/driver/neo4j_driver.py` and `graphiti_core/driver/neo4j/` operations
- Database name: Defaults to `neo4j` (configurable via `database` parameter)
- Transaction support: Managed via `AsyncSession.execute_write()` and `AsyncSession.run()`
- Features:
  - Fulltext search indices for entities, episodes, communities, edges
  - Cypher query execution
  - Support for Neo4j enterprise parallel runtime (via `USE_PARALLEL_RUNTIME` env var)

**FalkorDB:**
- Provider: FalkorDB 1.1.2+ (optional, `[falkordb]` extra)
- Protocol: Redis-compatible (runs on Redis)
- Connection: `redis://host:port` with optional password
- Async: Full async support via `falkordb.asyncio.FalkorDB`
- Client: `falkordb` package
- Implementation: `graphiti_core/driver/falkordb_driver.py` and `graphiti_core/driver/falkordb/` operations
- Database name: Defaults to `default_db` (configurable)
- Features:
  - Graph queries via Cypher
  - Fulltext search with stopwords (`graphiti_core/driver/falkordb/__init__.py`)
  - Web UI available (port 3000 in Docker)
  - Embedded in MCP server via Docker (preferred for local dev)

**Kuzu:**
- Provider: Kuzu 0.11.3+ (optional, `[kuzu]` extra)
- Type: In-process embedded graph database
- Client: `kuzu` package
- Implementation: `graphiti_core/driver/kuzu_driver.py`
- Features: No network dependency, suitable for development

**AWS Neptune:**
- Provider: AWS managed graph database (optional, `[neptune]` extra)
- Protocol: TLS over port 8182
- Clients: `boto3` (AWS SDK) + `opensearch-py` (search integration)
- Implementation: `graphiti_core/driver/neptune_driver.py` and `graphiti_core/driver/neptune/` operations
- Features: Managed service, high availability

**File Storage:**
- None configured for graph operations
- Optional: LLM response caching to local filesystem (`./llm_cache/` directory by default)

**Caching:**
- LLM Response Cache: File-based (optional, enabled via `cache=True` parameter in LLM clients)
- Location: `./llm_cache/` (configurable)
- Mechanism: MD5 hash of messages + model as cache key

## Authentication & Identity

**LLM Provider Auth:**
- OpenAI: API key in `OPENAI_API_KEY`
- Anthropic: API key in `ANTHROPIC_API_KEY`
- Gemini: API key in `GOOGLE_API_KEY`
- Groq: API key in `GROQ_API_KEY`
- Voyage: API key in `VOYAGE_API_KEY`

**Database Auth:**
- Neo4j: Username/password via constructor: `Neo4jDriver(uri, user, password)`
- FalkorDB: Optional password in URI: `redis://:password@host:port`

**Azure Auth:**
- Azure OpenAI: `azure-identity` package with DefaultAzureCredential (MCP server `[azure]` extra)
- Supports service principals, managed identity, interactive login

**No Session/JWT Management:**
- Graph service (`server/`) is stateless
- Clients handle their own authentication to external services

## Monitoring & Observability

**Error Tracking:**
- None configured by default (no Sentry, DataDog, etc.)
- PostHog telemetry enabled by default (can be disabled)

**Logging:**
- Python standard `logging` module
- Logger: `graphiti_core`, `graph_service`, `graphiti_mcp_server` namespaces
- Console output (configuration via `logging.config`)

**Distributed Tracing:**
- OpenTelemetry (optional, `[tracing]` extra)
- Packages: `opentelemetry-api>=1.20.0`, `opentelemetry-sdk>=1.20.0`
- Implementation: `graphiti_core/tracer.py` and `graphiti_core/telemetry/telemetry.py`
- Spans: LLM generation, graph operations (configurable)
- Support for OTEL exporters (configured externally via OTEL environment variables)

**Analytics:**
- PostHog: Product analytics client
- API key: Public key (safe to include in source)
- Host: `https://us.i.posthog.com`
- Implementation: `graphiti_core/telemetry/telemetry.py`
- Enable/Disable: `POSTHOG_DISABLED` environment variable

## CI/CD & Deployment

**Hosting:**
- Docker containers: `zepai/graphiti` (FastAPI server) and `zepai/knowledge-graph-mcp` (MCP server)
- Container registry: Docker Hub
- Platforms: linux/amd64, linux/arm64
- Manual ASGI server: Uvicorn (configured via Makefile, can use Gunicorn+Uvicorn)

**CI Pipeline:**
- GitHub Actions (workflows likely in `.github/workflows/` - not read per policy)
- Automated releases trigger Docker builds

**Build & Test:**
- No external CI service required (Makefile handles local testing)
- Test environment vars: `DISABLE_FALKORDB=1 DISABLE_KUZU=1 DISABLE_NEPTUNE=1` (skips optional DB tests)

## Environment Configuration

**Required Environment Variables:**

For Core Library:
- `OPENAI_API_KEY` - Must be set for LLM inference and embeddings

For Graph Service (server/):
- `OPENAI_API_KEY` - LLM provider
- `NEO4J_URI` - Database URI (e.g., `bolt://localhost:7687`)
- `NEO4J_USER` - Database username
- `NEO4J_PASSWORD` - Database password

For MCP Server:
- `OPENAI_API_KEY` or other LLM provider key
- `FALKORDB_URI` - Redis connection URI
- Optional: `FALKORDB_PASSWORD`, `CONFIG_PATH`, `GRAPHITI_GROUP_ID`

**Secrets Location:**
- Environment variables (local `.env` file, Docker environment, Kubernetes secrets)
- Never commit `.env` files or credential files
- `.gitignore` excludes `.env*` patterns

**Optional Environment Configuration:**
- `USE_PARALLEL_RUNTIME` - Enable Neo4j enterprise parallel runtime
- `SEMAPHORE_LIMIT` - Concurrency limit for async operations
- `EMBEDDING_DIM` - Embedding vector dimension
- Text chunking: `CHUNK_TOKEN_SIZE`, `CHUNK_OVERLAP_TOKENS`, `CHUNK_MIN_TOKENS`, `CHUNK_DENSITY_THRESHOLD`
- Index names: `ENTITY_INDEX_NAME`, `EPISODE_INDEX_NAME`, `COMMUNITY_INDEX_NAME`, `ENTITY_EDGE_INDEX_NAME`

## Webhooks & Callbacks

**Incoming:**
- FastAPI server endpoints in `server/graph_service/routers/`:
  - POST `/add_episode` - Ingest text/message/JSON data
  - GET `/search` - Hybrid search (semantic + keyword + graph traversal)
  - POST `/search` - Advanced search with filters
  - Other endpoints for entity/community queries

**Outgoing:**
- LLM API calls to OpenAI, Anthropic, Gemini, Groq (HTTP requests)
- Database queries to Neo4j, FalkorDB, Kuzu, Neptune (network requests)
- Embedding service calls to OpenAI, Voyage (HTTP requests)
- PostHog telemetry events (optional, can be disabled)
- OpenTelemetry export (if configured)

**No Webhook Support:**
- Graph service is request-response only
- No outbound webhook callbacks to external systems
- No webhook event subscriptions

---

*Integration audit: 2026-04-17*
