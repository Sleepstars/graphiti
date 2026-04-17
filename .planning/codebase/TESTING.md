# Testing Patterns

**Analysis Date:** 2026-04-17

## Test Framework

**Runner:**
- Framework: `pytest` v8.3.3+
- Async support: `pytest-asyncio` v0.24.0+
- Parallel execution: `pytest-xdist` v3.6.1+
- Config: `.planning/codebase/pytest.ini` in root (empty except pythonpath setting)
- Additional markers config: `tests/evals/pytest.ini` defines `integration` marker

**Assertion Library:**
- Python `assert` statements (built-in)
- NumPy assertions: `np.allclose()` for floating-point comparisons

**Run Commands:**
```bash
# Run unit tests only (skip integration tests)
DISABLE_FALKORDB=1 DISABLE_KUZU=1 DISABLE_NEPTUNE=1 uv run pytest -m "not integration"

# Run all tests with markers (integration and unit)
uv run pytest

# Watch mode with pytest
uv run pytest --watch

# Coverage report
uv run pytest --cov=graphiti_core --cov-report=html

# Run specific test file
uv run pytest tests/test_graphiti_mock.py

# Run specific test function
uv run pytest tests/test_graphiti_mock.py::test_add_bulk

# Run only integration tests
uv run pytest tests/ -k "_int" -v

# Run tests in parallel with pytest-xdist
uv run pytest -n auto
```

**Makefile commands:**
```bash
make test          # Run unit tests only (DISABLE_FALKORDB=1 DISABLE_KUZU=1 DISABLE_NEPTUNE=1)
make check         # Run format, lint, and test
```

## Test File Organization

**Location Patterns:**
- Unit tests: `tests/` directory, mirrors source structure
- Integration tests: Same files with `_int` suffix or `pytestmark = pytest.mark.integration`
- Evaluations: `tests/evals/` for end-to-end evaluation scripts

**Naming:**
- Test files: `test_*.py` or `*_test.py` (both used)
- Test functions: `test_*` (standard pytest convention)
- Integration tests: Suffixed with `_int` (e.g., `test_edge_int.py`)
- Test fixtures: Module-level fixtures in same file or in `helpers_test.py`

**Directory Structure:**
```
tests/
├── conftest.py                 # pytest configuration with fixtures
├── helpers_test.py             # Shared test utilities (fixtures, mock data)
├── test_add_triplet.py         # Unit tests
├── test_graphiti_mock.py       # Mock-based unit tests
├── test_edge_int.py            # Integration tests (requires DB)
├── test_entity_exclusion_int.py
├── test_graphiti_int.py
├── test_node_int.py
├── test_text_utils.py
├── test_node_label_security.py
├── cross_encoder/              # Reranker tests
│   ├── test_bge_reranker_client_int.py
│   ├── test_gemini_reranker_client.py
│   └── test_azure_openai_client.py
├── driver/                     # Database driver tests
│   └── test_falkordb_driver.py
├── embedder/                   # Embedding client tests
├── llm_client/                 # LLM client tests
│   ├── test_anthropic_client_int.py
│   ├── test_anthropic_client.py
│   ├── test_azure_openai_client.py
│   ├── test_cache.py
│   ├── test_gemini_client.py
│   └── test_groq_client.py
├── utils/
│   ├── search/
│   │   ├── search_utils_test.py
│   │   └── test_search_security.py
│   ├── maintenance/
│   │   ├── test_bulk_utils.py
│   │   ├── test_edge_operations.py
│   │   ├── test_entity_extraction.py
│   │   └── test_node_operations.py
│   └── test_content_chunking.py
└── evals/                      # Evaluation scripts
    ├── eval_e2e_graph_building.py
    ├── eval_cli.py
    └── utils.py
```

## Test Structure

**Suite Organization:**

Unit test structure in `test_graphiti_mock.py`:
```python
pytest_plugins = ('pytest_asyncio',)

@pytest.fixture
def mock_llm_client():
    """Create a mock LLM"""
    mock_llm = Mock(spec=LLMClient)
    mock_llm.config = Mock()
    mock_llm.model = 'test-model'
    # ... configure mock
    return mock_llm

@pytest.mark.asyncio
async def test_add_bulk(graph_driver, mock_llm_client, mock_embedder, mock_cross_encoder_client):
    # Setup
    graphiti = Graphiti(
        graph_driver=graph_driver,
        llm_client=mock_llm_client,
        embedder=mock_embedder,
        cross_encoder=mock_cross_encoder_client,
    )
    
    # Create test data
    entity_node = EntityNode(...)
    await entity_node.generate_name_embedding(mock_embedder)
    
    # Execute
    await add_nodes_and_edges_bulk(...)
    
    # Assert
    assert node_count == len(node_ids)
```

Integration test structure in `test_edge_int.py`:
```python
pytest_plugins = ('pytest_asyncio',)

@pytest.mark.asyncio
async def test_episodic_edge(graph_driver, mock_embedder):
    now = datetime.now()
    
    episode_node = EpisodicNode(...)
    await episode_node.save(graph_driver)
    
    node_count = await get_node_count(graph_driver, [episode_node.uuid])
    assert node_count == 1
```

**Patterns:**

Setup - `pytest_plugins = ('pytest_asyncio',)`:
- Enables async test support at module level
- Required for `@pytest.mark.asyncio` decorator to work

Fixtures:
- Module-level fixtures decorated with `@pytest.fixture`
- Parametrized fixtures: `@pytest.fixture(params=[...])` for multi-driver tests
- Scope: Default function scope (fresh for each test)

Async setup/teardown:
- Fixtures use `try/finally` for cleanup: `yield graph_driver; finally: await graph_driver.close()`

## Mocking

**Framework:** `unittest.mock` from Python standard library

**Patterns:**

Basic mock:
```python
from unittest.mock import Mock

mock_embedder = Mock(spec=EmbedderClient)
mock_embedder.create.side_effect = mock_embed
```

Async mock:
```python
from unittest.mock import AsyncMock

mock_driver = AsyncMock()
mock_driver.execute_query.return_value = [results, metadata, None]
```

Patching:
```python
from unittest.mock import patch

with patch('graphiti_core.search.search_utils.node_fulltext_search') as mock_fulltext:
    mock_fulltext.return_value = [EntityNode(...)]
    results = await hybrid_node_search(...)
```

**What to Mock:**
- External service calls (LLM APIs, embedders)
- Database drivers (unless running integration tests)
- Heavy computation (rerankers)

**What NOT to Mock:**
- Data structures (Pydantic models like `EntityNode`, `EntityEdge`)
- Validation logic
- Helper functions like `lucene_sanitize()`
- Graph traversal logic in integration tests

## Fixtures and Factories

**Test Data:**

Pre-generated embeddings dictionary in `helpers_test.py`:
```python
embedding_dim = 384
embeddings = {
    'Alice': [0.1, 0.2, ...],
    'Bob': [0.4, 0.5, ...],
    'Alice likes Bob': [0.7, 0.8, ...],
    # ... more entities
}

@pytest.fixture
def mock_embedder():
    mock_model = Mock(spec=EmbedderClient)
    
    def mock_embed(input_data):
        if isinstance(input_data, str):
            return embeddings[input_data]
        elif isinstance(input_data, list):
            combined = ' '.join(input_data)
            return embeddings[combined]
    
    mock_model.create.side_effect = mock_embed
    return mock_model
```

**Graph Driver Fixture with Parametrization:**

Multi-driver testing in `helpers_test.py`:
```python
drivers: list[GraphProvider] = []
if os.getenv('DISABLE_NEO4J') is None:
    drivers.append(GraphProvider.NEO4J)
if os.getenv('DISABLE_FALKORDB') is None:
    drivers.append(GraphProvider.FALKORDB)

@pytest.fixture(params=drivers)
async def graph_driver(request):
    driver = request.param
    graph_driver = get_driver(driver)
    await clear_data(graph_driver, [group_id, group_id_2])
    try:
        yield graph_driver
    finally:
        await graph_driver.close()
```

**Location:**
- `tests/helpers_test.py` - Centralized fixtures for all tests
- Module-specific fixtures: In the same test file or `conftest.py`
- Custom fixtures for specific domains: In domain-specific conftest files

## Coverage

**Requirements:** No coverage threshold enforced

**View Coverage:**
```bash
# Generate coverage report
uv run pytest --cov=graphiti_core --cov-report=html tests/

# View HTML report
open htmlcov/index.html
```

**Coverage tools:** Built-in pytest coverage plugin (when `--cov` flag used)

## Test Types

**Unit Tests:**
- Scope: Individual functions, validation logic, data structures
- Approach: Mock external dependencies (DB, LLM, embedders)
- Example: `test_graphiti_mock.py` tests graph building logic with mocked services
- No database required
- Fast execution

**Integration Tests:**
- Scope: Multi-component interactions with real database
- Approach: Use real graph drivers (Neo4j, FalkorDB, etc.)
- Marked with `pytestmark = pytest.mark.integration` or `_int` suffix
- Example: `test_edge_int.py` tests edge operations with actual database
- Requires database containers running
- Slower execution

**End-to-End Tests:**
- Location: `tests/evals/` directory
- Scope: Full application workflows
- Example: `eval_e2e_graph_building.py` - build knowledge graph from conversation data
- Used for evaluation and benchmarking
- Require real LLM APIs and databases

## Common Patterns

**Async Testing:**

Standard async test structure:
```python
@pytest.mark.asyncio
async def test_add_bulk(graph_driver, mock_llm_client, mock_embedder):
    graphiti = Graphiti(
        graph_driver=graph_driver,
        llm_client=mock_llm_client,
        embedder=mock_embedder,
    )
    
    node = EntityNode(name='Alice', ...)
    await node.generate_name_embedding(mock_embedder)
    await node.save(graph_driver)
```

Async coroutine gathering:
```python
from graphiti_core.helpers import semaphore_gather

subgraph_results = await semaphore_gather(
    *[
        build_subgraph(graphiti, user_id)
        for user_id in user_ids
    ]
)
```

**Error Testing:**

Custom exception assertions:
```python
from graphiti_core.errors import NodeNotFoundError

with pytest.raises(NodeNotFoundError):
    await NodeNotFoundError.get_by_uuid(driver, invalid_uuid)
```

**Assertion Helpers:**

Custom assertion functions in `helpers_test.py`:
```python
async def assert_entity_node_equals(
    graph_driver: GraphDriver,
    retrieved: EntityNode,
    sample: EntityNode
):
    await retrieved.load_name_embedding(graph_driver)
    assert retrieved.uuid == sample.uuid
    assert np.allclose(retrieved.name_embedding, sample.name_embedding)
```

## Multi-Driver Testing

**Parametrized fixtures for database backends:**

Tests run against multiple graph databases (Neo4j, FalkorDB, Kuzu):
```python
@pytest.fixture(params=drivers)
async def graph_driver(request):
    driver = request.param  # One of GraphProvider.NEO4J, GraphProvider.FALKORDB
    graph_driver = get_driver(driver)
    # ... setup and cleanup
```

**Skip test for specific driver:**
```python
@pytest.mark.asyncio
async def test_feature(graph_driver):
    if graph_driver.provider == GraphProvider.FALKORDB:
        pytest.skip('Feature not supported on FalkorDB')
```

**Environment variables for disabling drivers:**
- `DISABLE_NEO4J` - Skip Neo4j tests
- `DISABLE_FALKORDB` - Skip FalkorDB tests
- `DISABLE_KUZU` - Skip Kuzu tests
- `DISABLE_NEPTUNE` - Skip Neptune tests (disabled by default)

## Special Test Utilities

**Graph inspection helpers in `helpers_test.py`:**
```python
async def get_node_count(driver: GraphDriver, uuids: list[str]) -> int:
    """Count nodes by UUID list"""

async def get_edge_count(driver: GraphDriver, uuids: list[str]) -> int:
    """Count edges by UUID list"""

async def print_graph(graph_driver: GraphDriver):
    """Debug: Print all nodes and edges in graph"""
```

**Test data management:**
- `group_id = 'graphiti_test_group'` - Partition for test data
- `group_id_2 = 'graphiti_test_group_2'` - Secondary partition for multi-group tests
- All tests clean up data with `await clear_data(graph_driver, [group_id, group_id_2])`

## Server Tests (FastAPI)

**Server directory:** `/server/`
- Server has separate test infrastructure
- Run from `/server/` directory: `cd server && make test`
- Server uses same pytest framework with FastAPI-specific fixtures

---

*Testing analysis: 2026-04-17*
