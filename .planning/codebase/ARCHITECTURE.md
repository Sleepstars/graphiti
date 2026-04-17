# Architecture

**Analysis Date:** 2026-04-17

## Pattern Overview

**Overall:** Layered architecture with a temporal knowledge graph orchestrator pattern.

Graphiti uses a hub-and-spoke design where the `Graphiti` class orchestrates all interactions between pluggable components. The framework is designed for incremental, temporally-aware knowledge graph updates without batch recomputation.

**Key Characteristics:**
- **Pluggable clients**: LLM, embedder, cross-encoder, and graph driver are all injectable dependencies
- **Multi-backend database support**: Abstracted driver interface supporting Neo4j, FalkorDB, Kuzu, and Neptune
- **Temporal bi-temporal model**: Explicit tracking of event occurrence times and system times
- **Async-first design**: All I/O operations are async-compatible for concurrent processing
- **Modular extraction/resolution pipeline**: Separate extraction and deduplication steps with LLM-powered semantic resolution

## Layers

**Application Layer (Entry Points):**
- Purpose: Expose user-facing APIs for graph operations
- Location: `graphiti_core/graphiti.py` (Graphiti class), `server/` (REST API), `mcp_server/` (MCP endpoints)
- Contains: High-level methods like `add_episode()`, `add_triplet()`, `search()`
- Depends on: All core layers (clients, driver, utilities)
- Used by: External applications, FastAPI server, MCP server

**Orchestration Layer (Graphiti Class):**
- Purpose: Coordinate extraction, resolution, and persistence workflows
- Location: `graphiti_core/graphiti.py` (Graphiti class - 63KB, 1800+ lines)
- Contains: Workflow methods (`add_episode()`, `add_bulk_episodes()`, `search()`) that compose lower layers
- Depends on: Driver, LLM client, embedder, cross-encoder, search, utilities
- Used by: Server routers, MCP server, direct library consumers

**Client Layer (Pluggable Services):**
- **LLM Client** (`graphiti_core/llm_client/`): Abstract `LLMClient` with implementations for OpenAI, Anthropic, Gemini, Groq, Azure, and generic clients
  - Responsibilities: Generate structured output for extraction/deduplication using provider-specific APIs
  - Key files: `client.py` (base), `openai_client.py`, `anthropic_client.py`, `gemini_client.py`

- **Embedder Client** (`graphiti_core/embedder/`): Abstract `EmbedderClient` with implementations for OpenAI, Azure, Gemini, Voyage
  - Responsibilities: Generate vector embeddings for semantic search
  - Key files: `client.py` (base), `openai.py`, `gemini.py`

- **Cross-Encoder Client** (`graphiti_core/cross_encoder/`): Reranking for search results
  - Implementations: `OpenAIRerankerClient`, `NoopCrossEncoder`
  - Responsibilities: Re-rank search results by relevance

**Data Storage & Driver Layer:**
- Purpose: Abstract database operations and execute queries
- Location: `graphiti_core/driver/`
- Contains: Base `GraphDriver` with implementations for Neo4j, FalkorDB, Kuzu, Neptune
- Key files: `driver.py` (base interface), `neo4j_driver.py`, `falkordb_driver.py`, `kuzu_driver.py`, `neptune_driver.py`
- Responsibilities:
  - Execute parameterized queries against backend databases
  - Manage connections and transactions
  - Provide node/edge operation interfaces (via operations submodule)
  - Build indices and constraints

**Operations Layer:**
- Purpose: Database-specific CRUD operations for graph elements
- Location: `graphiti_core/driver/operations/`
- Contains: Separated operation classes for each node/edge type:
  - `entity_node_ops.py`, `community_node_ops.py`, `episode_node_ops.py`, `saga_node_ops.py`
  - `entity_edge_ops.py`, `episodic_edge_ops.py`, `has_episode_edge_ops.py`, `next_episode_edge_ops.py`
  - `search_ops.py`, `graph_ops.py` (maintenance operations)
- Used by: Node/edge namespaces, Graphiti orchestrator

**Model Layer (Graph Elements):**
- Purpose: Define graph node and edge types with persistence logic
- Location: `graphiti_core/nodes.py`, `graphiti_core/edges.py`
- Contains:
  - **Nodes**: `EntityNode`, `EpisodicNode`, `CommunityNode`, `SagaNode` (all inherit from base `Node`)
  - **Edges**: `EntityEdge`, `EpisodicEdge`, `HasEpisodeEdge`, `NextEpisodeEdge`, `CommunityEdge`
  - Each model has `save()` and `delete()` methods that interact with the driver
- Depends on: Embedder (for generating embeddings before save)
- Used by: Extraction/resolution logic, namespaces

**Namespace Layer (User-Facing Direct API):**
- Purpose: Provide direct object-oriented API for node/edge manipulation
- Location: `graphiti_core/namespaces/nodes.py`, `graphiti_core/namespaces/edges.py`
- Contains: Namespace classes (`NodeNamespace`, `EdgeNamespace` with sub-namespaces for each type)
- Usage: `graphiti.nodes.entity.save()`, `graphiti.edges.entity.save()`
- Depends on: Operations layer, embedder

**Search Layer:**
- Purpose: Implement hybrid search combining semantic embeddings, BM25, and graph traversal
- Location: `graphiti_core/search/`
- Key files:
  - `search.py`: Main `search()` function orchestrating different strategies
  - `search_config.py`: Configuration for search behavior (node/edge/community/episode search types)
  - `search_config_recipes.py`: Pre-built search configurations (e.g., `COMBINED_HYBRID_SEARCH_CROSS_ENCODER`)
  - `search_filters.py`: Filtering mechanisms for search
  - `search_utils.py`: Implementation of search strategies (BFS, BM25, semantic, MMR, RRF)
- Search strategies: Cosine similarity, fulltext (BM25), breadth-first search, maximal marginal relevance, reciprocal rank fusion
- Rerankers: Distance-based, mention-based, MMR

**Extraction & Resolution Layer:**
- Purpose: Extract entities and relationships from content, then resolve/deduplicate them
- Location: `graphiti_core/utils/maintenance/`
- Key files:
  - `node_operations.py`: `extract_nodes()`, `resolve_extracted_nodes()` - extract entities and deduplicate
  - `edge_operations.py`: `extract_edges()`, `resolve_extracted_edges()` - extract relationships
  - `community_operations.py`: `build_communities()`, `update_community()` - community detection
  - `graph_data_operations.py`: Retrieve episodes, maintenance operations
  - `dedup_helpers.py`: Deduplication utilities

**Prompts Layer:**
- Purpose: Define LLM prompts for extraction, deduplication, summarization
- Location: `graphiti_core/prompts/`
- Key files:
  - `extract_nodes.py`: Prompt for entity extraction (returns structured JSON)
  - `extract_edges.py`: Prompt for relationship extraction
  - `dedupe_nodes.py`: Prompt for node deduplication using LLM semantic comparison
  - `dedupe_edges.py`: Prompt for edge deduplication
  - `summarize_nodes.py`: Summarization instructions
  - `lib.py`, `models.py`: Shared prompt utilities and message models

**Utility Layer:**
- Purpose: Support operations and helpers
- Location: `graphiti_core/utils/`
- Key files:
  - `bulk_utils.py`: Bulk ingestion operations (`add_nodes_and_edges_bulk()`, `extract_nodes_and_edges_bulk()`)
  - `content_chunking.py`: Text chunking strategies for large content
  - `datetime_utils.py`: Temporal utilities (UTC handling)
  - `text_utils.py`: Text processing helpers

**Telemetry & Tracing Layer:**
- Purpose: Optional distributed tracing and telemetry
- Location: `graphiti_core/telemetry/`, `graphiti_core/tracer.py`
- Contains: OpenTelemetry integration and no-op tracer for disabled tracing
- Optional: Only active if OpenTelemetry is configured

## Data Flow

**Episode Ingestion Pipeline (add_episode):**

1. **Validation**: Validate entity types, excluded types, group ID
2. **Episode Creation**: Create `EpisodicNode` with reference time and source type
3. **Saga Handling** (optional): Get or create `SagaNode` and link episode
4. **Previous Episodes**: Retrieve recent episodes for context (temporal window = 10 by default)
5. **Node Extraction**: 
   - Call LLM to extract entities from episode content with custom schema
   - Returns structured JSON with entity type, name, and description
6. **Node Resolution**:
   - Compare extracted nodes against existing nodes using embeddings and LLM semantic matching
   - Create new `EntityNode` objects for unmatched entities
   - Return mapping of extracted→resolved UUIDs
7. **Edge Extraction**:
   - Call LLM to extract relationships between extracted entities
   - Returns structured JSON with source, target, and relationship type
8. **Edge Resolution**:
   - Resolve edge pointers using node UUID mapping
   - Check for existing edges and mark for invalidation if new info differs
   - Return resolved edges, invalidated edges, new edges
9. **Edge Invalidation** (optional): Mark old edges as invalidated if superseded
10. **Community Updates** (optional): Rebuild community nodes with new entities
11. **Persistence**:
    - Generate embeddings for new nodes (name + description)
    - Save nodes to database via driver
    - Create `HasEpisodeEdge` linking episode to entities and `NextEpisodeEdge` for saga sequence
    - Save edges to database
12. **Return**: `AddEpisodeResults` containing created/updated nodes, edges, communities

**Search Pipeline (search):**

1. **Configuration**: Receive search config specifying which search methods and rerankers to use
2. **Embedding** (if semantic search requested): Generate embedding for query string
3. **Parallel Execution**: Run configured search strategies in parallel:
   - **Node Search**: Semantic, fulltext, or BFS
   - **Edge Search**: Semantic, fulltext, or BFS
   - **Community Search**: Semantic or fulltext
   - **Episode Search**: Fulltext or mentions
4. **Combination**: Merge results using configured ranking (reciprocal rank fusion, distance-based, etc.)
5. **Reranking** (optional): Use cross-encoder to rerank final results
6. **Filtering**: Apply search filters (node labels, edge types, timestamps)
7. **Return**: `SearchResults` containing matched nodes, edges, communities, episodes

**State Management:**
- **Node/Edge UUIDs**: Immutable identifiers for tracking entities across episodes
- **Created/Updated timestamps**: Bi-temporal: `created_at` (occurrence time) and database insertion time
- **Invalidation**: Old edges marked with `invalid_from` timestamp when superseded
- **Group IDs**: Partition graphs for multi-tenant support
- **Embeddings**: Stored on nodes for semantic search (updated only on save)

## Key Abstractions

**GraphDriver:**
- Purpose: Abstract all database operations
- Implementations: `Neo4jDriver`, `FalkorDBDriver`, `KuzuDriver`, `NeptuneDriver`
- Pattern: Each driver implements the base interface with database-specific query execution
- Example usage: `await driver.execute_query(query, **params)`

**LLMClient:**
- Purpose: Provide structured output from LLMs for extraction/deduplication
- Pattern: Base class defines interface; subclasses override for provider-specific behavior
- Key method: `async def get_structured_output(...)` → returns Pydantic model instances

**SearchConfig:**
- Purpose: Declarative configuration for search strategies
- Pattern: Configuration objects specify which search methods (`fulltext`, `cosine_similarity`, `bfs`) and rerankers to use
- Pre-built recipes: `COMBINED_HYBRID_SEARCH_CROSS_ENCODER`, `EDGE_HYBRID_SEARCH_RRF`

**Node/Edge Models:**
- Purpose: Represent graph elements with methods for persistence
- Pattern: Pydantic models with `async def save(driver)` and `async def delete(driver)` methods
- Subclasses: Type-specific versions (EntityNode, EpisodicNode, etc.)

**Namespace:**
- Purpose: Provide object-oriented API for direct operations
- Pattern: Thin wrapper around operations layer for ergonomic API
- Example: `graphiti.nodes.entity.save(node)` delegates to `EntityNodeNamespace.save()`

## Entry Points

**Graphiti Class (Library):**
- Location: `graphiti_core/graphiti.py`
- Key methods:
  - `add_episode()` - Single episode ingestion with LLM extraction
  - `add_bulk_episodes()` - Batch episode processing
  - `add_triplet()` - Direct (subject, relation, object) ingestion
  - `search()` - Query the knowledge graph
  - `build_indices_and_constraints()` - Database initialization
- Triggers: Direct instantiation and method calls by applications

**FastAPI Server:**
- Location: `server/graph_service/main.py`
- Entry point: `app` (FastAPI instance)
- Routers:
  - `graph_service/routers/ingest.py` - POST `/add_episode`, `/add_bulk_episodes`
  - `graph_service/routers/retrieve.py` - GET `/search`
- Triggers: HTTP requests to REST endpoints

**MCP Server:**
- Location: `mcp_server/src/graphiti_mcp_server.py`
- Entry point: Model Context Protocol server for AI assistants
- Tools: Search, add memory, manage knowledge
- Triggers: MCP client requests (Claude, other AI assistants)

## Error Handling

**Strategy:** Custom exception hierarchy with specific error types for precise error handling.

**Patterns:**
- `NodeNotFoundError`: Raised when searching for non-existent nodes
- `EdgeNotFoundError`: Raised when searching for non-existent edges
- `SearchRerankerError`: Raised when cross-encoder reranking fails
- `RateLimitError`: Rate limit from LLM provider
- Validation errors: Pydantic raises `ValidationError` for invalid inputs
- Database errors: Provider-specific errors bubble up (Neo4j `DriverError`, etc.)

**Handling approach:**
- Type extraction and resolution use `extract_nodes()` / `resolve_extracted_nodes()` which catch LLM errors and may return partial results
- Search errors are caught and logged; partial results returned if reranking fails
- Application layer catches and transforms errors for API responses (in `server/`)

## Cross-Cutting Concerns

**Logging:** 
- Uses Python `logging` module configured per module
- Log level controlled via environment or configuration
- Key loggers: `graphiti_core.graphiti`, `graphiti_core.llm_client`, `graphiti_core.driver.driver`

**Validation:** 
- Pydantic models validate all inputs at construction
- Custom validators on Node/Edge models (e.g., labels validation)
- Helper functions: `validate_entity_types()`, `validate_group_id()`, `validate_group_ids()`

**Authentication:** 
- Delegated to database drivers (Neo4j credentials passed to Neo4jDriver)
- LLM API keys managed via environment variables (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
- No authentication layer in Graphiti itself; assumes secure deployment

**Concurrency:**
- Uses async/await throughout for I/O operations
- `semaphore_gather()` utility limits concurrent operations (configurable `SEMAPHORE_LIMIT`)
- Database operations may use transactions for atomicity

**Telemetry:**
- Optional OpenTelemetry tracing via `tracer.py`
- No-op tracer used when disabled
- Tracks events like `graphiti_initialized` via PostHog

---

*Architecture analysis: 2026-04-17*
