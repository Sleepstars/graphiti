# Codebase Structure

**Analysis Date:** 2026-04-17

## Directory Layout

```
graphiti/
├── graphiti_core/              # Core library implementation
│   ├── graphiti.py             # Main Graphiti orchestrator class
│   ├── nodes.py                # Node model definitions (Entity, Episodic, Community, Saga)
│   ├── edges.py                # Edge model definitions (EntityEdge, EpisodicEdge, etc.)
│   ├── driver/                 # Database abstraction layer
│   │   ├── driver.py           # Base GraphDriver interface
│   │   ├── neo4j_driver.py     # Neo4j implementation
│   │   ├── falkordb_driver.py  # FalkorDB implementation
│   │   ├── kuzu_driver.py      # Kuzu implementation
│   │   ├── neptune_driver.py   # Neptune implementation
│   │   ├── operations/         # CRUD operations for each node/edge type
│   │   ├── graph_operations/   # Graph maintenance operations interface
│   │   ├── search_interface/   # Search operations interface
│   │   ├── neo4j/              # Neo4j-specific implementations
│   │   ├── falkordb/           # FalkorDB-specific implementations
│   │   ├── kuzu/               # Kuzu-specific implementations
│   │   └── neptune/            # Neptune-specific implementations
│   ├── llm_client/             # LLM provider clients
│   │   ├── client.py           # Abstract LLMClient base class
│   │   ├── openai_client.py    # OpenAI implementation
│   │   ├── anthropic_client.py # Anthropic (Claude) implementation
│   │   ├── gemini_client.py    # Google Gemini implementation
│   │   ├── groq_client.py      # Groq implementation
│   │   ├── azure_openai_client.py # Azure OpenAI implementation
│   │   ├── openai_base_client.py  # Shared OpenAI base logic
│   │   ├── gliner2_client.py   # GLiNER2 local entity extraction
│   │   ├── token_tracker.py    # Token usage tracking
│   │   └── cache.py            # LLM response caching
│   ├── embedder/               # Embedding provider clients
│   │   ├── client.py           # Abstract EmbedderClient base class
│   │   ├── openai.py           # OpenAI embeddings
│   │   ├── azure_openai.py     # Azure OpenAI embeddings
│   │   ├── gemini.py           # Google Gemini embeddings
│   │   └── voyage.py           # Voyage AI embeddings
│   ├── cross_encoder/          # Reranking clients
│   │   ├── client.py           # Abstract CrossEncoderClient
│   │   ├── openai_reranker_client.py # OpenAI reranker
│   │   └── noop_client.py      # No-op reranker (disabled)
│   ├── search/                 # Hybrid search implementation
│   │   ├── search.py           # Main search orchestrator
│   │   ├── search_config.py    # Search configuration models
│   │   ├── search_config_recipes.py # Pre-built search configs
│   │   ├── search_filters.py   # Search filtering
│   │   ├── search_utils.py     # Search strategy implementations
│   │   └── search_helpers.py   # Search helper functions
│   ├── prompts/                # LLM prompts for extraction/deduplication
│   │   ├── extract_nodes.py    # Entity extraction prompt
│   │   ├── extract_edges.py    # Relationship extraction prompt
│   │   ├── dedupe_nodes.py     # Node deduplication prompt
│   │   ├── dedupe_edges.py     # Edge deduplication prompt
│   │   ├── summarize_nodes.py  # Node summarization prompt
│   │   ├── lib.py              # Prompt template library
│   │   ├── models.py           # Message models for prompts
│   │   └── prompt_helpers.py   # Prompt utilities
│   ├── utils/                  # Utility functions
│   │   ├── bulk_utils.py       # Bulk ingestion operations
│   │   ├── content_chunking.py # Text chunking strategies
│   │   ├── datetime_utils.py   # Datetime handling (UTC)
│   │   ├── text_utils.py       # Text processing utilities
│   │   └── maintenance/        # Maintenance and data operations
│   │       ├── node_operations.py      # Extract/resolve nodes
│   │       ├── edge_operations.py      # Extract/resolve edges
│   │       ├── community_operations.py # Community detection
│   │       ├── graph_data_operations.py # Retrieve episodes
│   │       └── dedup_helpers.py        # Deduplication utilities
│   ├── models/                 # Database query definitions
│   │   ├── nodes/
│   │   │   └── node_db_queries.py # Node save/retrieve queries
│   │   └── edges/
│   │       └── edge_db_queries.py # Edge save/retrieve queries
│   ├── namespaces/             # User-facing object API
│   │   ├── nodes.py            # Node namespaces (entity, episode, community, saga)
│   │   └── edges.py            # Edge namespaces (entity, episodic, has_episode, etc.)
│   ├── telemetry/              # Telemetry and event tracking
│   ├── tracer.py               # OpenTelemetry integration
│   ├── decorators.py           # Decorators (group_id handling)
│   ├── errors.py               # Custom exception hierarchy
│   ├── graphiti_types.py       # Type definitions
│   ├── graph_queries.py        # Utility queries
│   ├── helpers.py              # Helper functions
│   └── migrations/             # Database migrations
├── server/                     # FastAPI REST API service
│   ├── graph_service/
│   │   ├── main.py             # FastAPI app setup
│   │   ├── config.py           # Server configuration
│   │   ├── llm_compat.py       # LLM compatibility layer
│   │   ├── zep_graphiti.py     # Graphiti initialization
│   │   ├── dto/                # Data transfer objects
│   │   │   ├── ingest_dto.py   # Request/response schemas
│   │   │   └── search_dto.py   # Search request/response
│   │   └── routers/
│   │       ├── ingest.py       # Episode ingestion endpoints
│   │       └── retrieve.py     # Search endpoints
│   └── pyproject.toml          # Server dependencies
├── mcp_server/                 # Model Context Protocol server
│   ├── src/
│   │   └── graphiti_mcp_server.py # MCP server implementation
│   ├── config/                 # MCP configuration
│   ├── docker/                 # Docker setup
│   ├── docs/                   # Documentation
│   ├── tests/                  # MCP tests
│   └── docker-compose.yml      # MCP docker compose
├── tests/                      # Test suite
│   ├── test_graphiti.py        # Core Graphiti tests
│   ├── driver/                 # Driver-specific tests
│   ├── embedder/               # Embedder tests
│   ├── llm_client/             # LLM client tests
│   ├── cross_encoder/          # Cross-encoder tests
│   ├── utils/                  # Utility tests
│   │   ├── maintenance/        # Maintenance operation tests
│   │   └── search/             # Search tests
│   └── evals/                  # Evaluation scripts
├── examples/                   # Usage examples
│   ├── quickstart/             # Quick start example
│   ├── opentelemetry/          # Tracing example
│   ├── podcast/                # Podcast ingestion example
│   ├── wizard_of_oz/           # Multi-party conversation example
│   ├── langgraph-agent/        # LangGraph integration
│   ├── azure-openai/           # Azure OpenAI example
│   ├── ecommerce/              # E-commerce domain example
│   ├── gliner2/                # GLiNER2 extraction example
│   └── data/                   # Example data files
├── signatures/                 # Specification files
├── spec/                       # OpenAPI/spec files
├── .github/                    # GitHub workflows and config
├── graphiti_core/__init__.py   # Package exports
├── pyproject.toml              # Main project config
├── Makefile                    # Development commands
├── CLAUDE.md                   # Claude development guide
├── README.md                   # Project documentation
├── docker-compose.yml          # Local development environment
├── docker-compose.test.yml     # Test environment
└── Dockerfile                  # Production dockerfile
```

## Directory Purposes

**graphiti_core/:**
- Purpose: Core library containing all knowledge graph logic
- Contains: Orchestrator, drivers, clients, models, search, extraction
- Key concept: Self-contained, reusable library with minimal external dependencies

**graphiti_core/driver/:**
- Purpose: Database abstraction layer
- Contains: Base `GraphDriver` interface and database-specific implementations
- Backend support: Neo4j, FalkorDB, Kuzu, Neptune
- Structure: Common `operations/` directory with shared operation classes; backend-specific folders for driver implementations
- Usage: All database I/O goes through driver interface for portability

**graphiti_core/llm_client/:**
- Purpose: LLM provider integration
- Contains: Abstract base class and provider-specific clients
- Providers: OpenAI (default), Anthropic, Google Gemini, Groq, Azure, and local GLiNER2
- Common pattern: Each client wraps provider API and returns structured Pydantic models

**graphiti_core/embedder/:**
- Purpose: Vector embedding generation
- Contains: Abstract `EmbedderClient` with provider implementations
- Providers: OpenAI, Azure, Gemini, Voyage
- Usage: Embeddings stored on nodes for semantic search; generated on node creation

**graphiti_core/search/:**
- Purpose: Hybrid search combining multiple ranking strategies
- Contains: Search orchestrator, configuration system, and strategy implementations
- Strategies: Semantic (cosine), fulltext (BM25), BFS, MMR, RRF
- Extensibility: New search configs can be defined in `search_config_recipes.py`

**graphiti_core/prompts/:**
- Purpose: LLM prompts for extraction, deduplication, summarization
- Contains: Pydantic model schemas and prompt templates
- Structure: One file per major LLM task (extract nodes, extract edges, dedupe, etc.)
- Pattern: Each prompt defines output schema and instruction string

**graphiti_core/utils/maintenance/:**
- Purpose: Complex graph operations requiring orchestration
- Contains: Node/edge extraction and resolution, community detection, episode retrieval
- Key functions:
  - `extract_nodes()`: LLM-based entity extraction
  - `resolve_extracted_nodes()`: Semantic deduplication against existing nodes
  - `extract_edges()`: LLM-based relationship extraction
  - `resolve_extracted_edges()`: Deduplication and invalidation of old edges
  - `build_communities()`: Community detection algorithm
  - `retrieve_episodes()`: Query historical episodes

**graphiti_core/namespaces/:**
- Purpose: User-facing object-oriented API
- Contains: Thin wrappers around operations for ergonomic access
- Usage pattern: `graphiti.nodes.entity.save(node)` instead of lower-level operation calls
- Benefit: Cleaner API surface; operations remain composable for internal use

**server/:**
- Purpose: REST API wrapper around Graphiti library
- Contains: FastAPI app, routers for ingest/search, DTOs for request/response
- Deployment: Standalone service deployable to container/cloud
- Entry point: `server/graph_service/main.py` (FastAPI app)

**mcp_server/:**
- Purpose: Model Context Protocol integration for AI assistants (Claude, etc.)
- Contains: MCP tool definitions, service layer, Docker setup
- Deployment: Containerized with Neo4j; runs as MCP server
- Tools exposed: Search knowledge graph, add memory, manage preferences

**tests/:**
- Purpose: Comprehensive test suite
- Structure: Mirrors source structure; tests named `test_*.py` or `*_test.py`
- Markers: Integration tests marked with `_int` suffix (require database)
- Execution: Unit tests runnable without external services; integration tests need Neo4j/FalkorDB

**examples/:**
- Purpose: Usage demonstrations
- Contents: Complete working examples showing common patterns
- Key examples:
  - `quickstart/`: Basic episode ingestion and search
  - `wizard_of_oz/`: Multi-party conversation tracking
  - `langgraph-agent/`: LangGraph AI agent integration
  - `opentelemetry/`: Distributed tracing setup

## Key File Locations

**Entry Points:**
- `graphiti_core/graphiti.py`: Main `Graphiti` class (library entry point)
- `server/graph_service/main.py`: REST API entry point
- `mcp_server/src/graphiti_mcp_server.py`: MCP server entry point

**Configuration:**
- `pyproject.toml`: Project dependencies, build config, tool settings
- `server/graph_service/config.py`: Server environment configuration
- `mcp_server/config/`: MCP server configuration files

**Core Logic:**
- `graphiti_core/graphiti.py`: Orchestration (episode ingestion, search, bulk operations)
- `graphiti_core/nodes.py`: All node types and persistence logic
- `graphiti_core/edges.py`: All edge types and persistence logic

**Search & Query:**
- `graphiti_core/search/search.py`: Main search function
- `graphiti_core/search/search_config.py`: Search configuration types
- `graphiti_core/search/search_utils.py`: Search strategy implementations (73KB file with all ranking algorithms)

**Extraction & Resolution:**
- `graphiti_core/utils/maintenance/node_operations.py`: Entity extraction and deduplication
- `graphiti_core/utils/maintenance/edge_operations.py`: Relationship extraction
- `graphiti_core/utils/maintenance/community_operations.py`: Community detection

**Prompts:**
- `graphiti_core/prompts/extract_nodes.py`: Entity extraction schema and prompt
- `graphiti_core/prompts/extract_edges.py`: Relationship extraction schema
- `graphiti_core/prompts/dedupe_nodes.py`: Semantic deduplication prompt

**Database:**
- `graphiti_core/driver/driver.py`: Base `GraphDriver` interface (100+ lines)
- `graphiti_core/driver/neo4j_driver.py`: Neo4j implementation
- `graphiti_core/driver/operations/`: All CRUD operation implementations

## Naming Conventions

**Files:**
- Library files: `snake_case.py` (e.g., `llm_client.py`, `search_utils.py`)
- Driver implementations: `{backend}_driver.py` (e.g., `neo4j_driver.py`, `falkordb_driver.py`)
- Operation files: `{type}_ops.py` (e.g., `entity_node_ops.py`, `search_ops.py`)
- Test files: `test_{module}.py` or `{module}_test.py` (e.g., `test_graphiti.py`)

**Directories:**
- Feature areas: `plural_noun/` (e.g., `driver/`, `prompts/`, `utils/`)
- Implementations: `backend_name/` for database-specific code
- Operations: `operations/` for CRUD implementations

**Classes:**
- PascalCase: `Graphiti`, `GraphDriver`, `EntityNode`, `EntityEdge`
- Abstract bases: Prefix or suffix convention (e.g., `LLMClient` base, `Neo4jDriver` implementation)

**Functions:**
- camelCase (internal/private): `_extract_nodes()`, `_resolve_nodes()`
- snake_case (public): `add_episode()`, `search()`, `extract_nodes()`
- Async operations: Prefix with `async def`, no special naming

**Variables:**
- camelCase (inside functions/methods): `episodeBody`, `groupId`
- snake_case (module/class attributes): `store_raw_episode_content`, `max_coroutines`
- Constants: UPPER_SNAKE_CASE: `DEFAULT_SEARCH_LIMIT`, `EPISODE_WINDOW_LEN`

**Models & Types:**
- Pydantic models: PascalCase with `Node`/`Edge` suffix: `EntityNode`, `EpisodicEdge`
- Configuration: PascalCase with `Config` suffix: `SearchConfig`, `LLMConfig`
- DTOs: PascalCase with `DTO` or domain suffix: `IngestEpisodeDTO`, `SearchResultsDTO`

## Where to Add New Code

**New Feature (e.g., custom extraction):**
- Primary code: `graphiti_core/{feature_name}/`
- Tests: `tests/{feature_name}/test_{module}.py`
- Integration with Graphiti class: Add method to `graphiti_core/graphiti.py`
- Example: Custom entity extractor → `graphiti_core/entity_extraction/custom_extractor.py`

**New LLM Provider:**
- Implementation: `graphiti_core/llm_client/{provider_name}_client.py`
- Base class: Inherit from `LLMClient` in `graphiti_core/llm_client/client.py`
- Export: Add to `graphiti_core/llm_client/__init__.py`
- Example: Groq → `graphiti_core/llm_client/groq_client.py`

**New Database Backend:**
- Driver implementation: `graphiti_core/driver/{backend_name}_driver.py`
- Operations: Implement operations in `graphiti_core/driver/operations/`
- Backend-specific code: `graphiti_core/driver/{backend_name}/` directory
- Register: Add to `GraphProvider` enum in `graphiti_core/driver/driver.py`

**New Search Strategy:**
- Implementation: Add function to `graphiti_core/search/search_utils.py`
- Configuration: Add `{NodeType}SearchMethod` enum variant in `graphiti_core/search/search_config.py`
- Recipe: Define pre-built config in `graphiti_core/search/search_config_recipes.py`
- Integration: Add case in `search()` function in `graphiti_core/search/search.py`

**Utilities:**
- Shared helpers: `graphiti_core/utils/{area}_utils.py`
- Maintenance operations: `graphiti_core/utils/maintenance/{operation_type}.py`
- Data models/queries: `graphiti_core/models/{category}/` (nodes, edges)

**Tests:**
- Unit tests: `tests/test_{module}.py`
- Integration tests: `tests/{area}/test_{module}_int.py` (includes `_int` suffix)
- Fixtures: `tests/conftest.py` or `tests/{area}/conftest.py`
- Example: New node tests → `tests/test_nodes.py`, integration tests → `tests/test_nodes_int.py`

## Special Directories

**graphiti_core/migrations/:**
- Purpose: Database schema versioning and migrations
- Generated: No
- Committed: Yes
- Usage: Applied during database setup for backwards compatibility

**graphiti_core/cross_encoder/:**
- Purpose: Result reranking implementations
- Key file: `client.py` (base class)
- Implementations: `openai_reranker_client.py`, `noop_client.py`

**graphiti_core/namespaces/:**
- Purpose: User-facing API with namespace pattern
- Note: Thin wrappers; actual logic in operations layer
- Usage: `graphiti.nodes.entity.save()` pattern

**server/graph_service/dto/:**
- Purpose: Request/response schemas for REST API
- Pattern: Pydantic models for validation and serialization
- Usage: FastAPI endpoint parameters and returns

**mcp_server/config/:**
- Purpose: MCP server configuration
- Contains: Connection strings, server settings
- Note: Secrets should use environment variables

**tests/evals/:**
- Purpose: End-to-end evaluation scripts
- Contents: Benchmark data, evaluation harness
- Not part of main test suite; run separately for performance validation

---

*Structure analysis: 2026-04-17*
