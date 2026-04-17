# Coding Conventions

**Analysis Date:** 2026-04-17

## Naming Patterns

**Files:**
- Modules: lowercase with underscores (e.g., `graphiti.py`, `llm_client.py`, `neo4j_driver.py`)
- Test files: `test_*.py` or `*_test.py` (both patterns used)
- Integration tests: `*_int.py` suffix (e.g., `test_edge_int.py`, `test_entity_exclusion_int.py`)
- Evaluation scripts: `eval_*.py` (e.g., `eval_e2e_graph_building.py`)

**Functions:**
- Snake case: `lucene_sanitize()`, `validate_group_id()`, `semaphore_gather()`
- Async functions prefixed contextually, no special naming convention beyond snake_case
- Private/internal functions: standard snake case (no leading underscore convention strictly enforced)

**Variables:**
- Snake case throughout: `group_id`, `source_node_uuid`, `embeddings`, `mock_embedder`
- Constants: SCREAMING_SNAKE_CASE (e.g., `SEMAPHORE_LIMIT`, `DEFAULT_PAGE_LIMIT`, `CHUNK_TOKEN_SIZE`)
- Protected constants: single leading underscore before usage (e.g., `SAFE_CYPHER_IDENTIFIER_PATTERN`)

**Types:**
- PascalCase for classes: `Node`, `EntityNode`, `EpisodicNode`, `GraphDriver`
- Enum members: lowercase (e.g., `EpisodeType.message`, `EpisodeType.json`)
- Type aliases: Follow standard Python conventions

## Code Style

**Formatting:**
- Tool: `ruff` (via `uv run ruff`)
- Line length: 100 characters (configured in `pyproject.toml`)
- Quote style: Single quotes preferred (`quote-style = "single"`)
- Indentation: 4 spaces (space indentation)
- Docstring formatting: Enabled for code blocks (`docstring-code-format = true`)

**Linting:**
- Tool: `ruff` for formatting and linting
- Type checking: `pyright` (enforced via `make lint`)
- Main project: `typeCheckingMode = "basic"` in `pyproject.toml`
- Linting includes:
  - pycodestyle (E)
  - Pyflakes (F)
  - pyupgrade (UP)
  - flake8-bugbear (B)
  - flake8-simplify (SIM)
  - isort import sorting (I)
- Ignored rules: `E501` (line length - handled by formatter)

**Special linting rule:**
- `typing.TypedDict` banned - must use `typing_extensions.TypedDict` instead (required for Python < 3.12 compatibility)

## Import Organization

**Order:**
1. Standard library (e.g., `import os`, `from datetime import datetime`, `from abc import ABC`)
2. Third-party packages (e.g., `from pydantic import BaseModel`, `import numpy as np`)
3. Local project imports (e.g., `from graphiti_core.driver.driver import GraphDriver`)

**Path Aliases:**
None configured. Imports use full relative module paths from project root.

**Examples:**
```python
# Standard library
import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from uuid import uuid4

# Third-party
import numpy as np
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing_extensions import LiteralString

# Local
from graphiti_core.driver.driver import GraphDriver, GraphProvider
from graphiti_core.embedder import EmbedderClient
from graphiti_core.helpers import validate_node_labels
```

## Error Handling

**Patterns:**
- Custom exception hierarchy: All exceptions inherit from `GraphitiError`
- Exceptions are defined in `graphiti_core/errors.py`
- Exceptions include context in `__init__` and store a `message` attribute
- Exceptions are used for validation errors (e.g., `NodeNotFoundError`, `GroupIdValidationError`)

**Exception Examples:**
```python
class NodeNotFoundError(GraphitiError):
    def __init__(self, uuid: str):
        self.message = f'node {uuid} not found'
        super().__init__(self.message)

class NodeLabelValidationError(GraphitiError, ValueError):
    def __init__(self, node_labels: list[str]):
        label_list = ', '.join(f'"{label}"' for label in node_labels)
        self.message = f'node_labels must start with a letter...: {label_list}'
        super().__init__(self.message)
```

**Validation Pattern:**
- Validation functions return `True` on success, raise exceptions on failure
- Example: `validate_group_id()` raises `GroupIdValidationError`, otherwise returns `True`
- Used with Pydantic `@field_validator` decorators

## Logging

**Framework:** Standard `logging` module

**Patterns:**
- Module-level logger: `logger = logging.getLogger(__name__)`
- Log levels used: DEBUG, INFO, ERROR
- Debug logging for operational details: `logger.debug(f'Deleted Edge: {self.uuid}')`
- Error logging for failures: `logger.error(f'Episode type: {episode_type} not implemented')`

**Example:**
```python
import logging

logger = logging.getLogger(__name__)

logger.error(f'Episode type: {episode_type} not implemented')
logger.debug(f'Deleted Edge: {self.uuid}')
```

## Comments

**When to Comment:**
- Complex algorithms or non-obvious business logic
- Configuration explanations (e.g., density-based chunking thresholds)
- Special handling for multiple database backends
- Temporal annotations and temporal data model explanations

**JSDoc/TSDoc:**
- Not used (Python project)
- Docstrings: Used for classes, functions, and enums with comprehensive explanations
- Docstring format: Google-style with Args, Returns, Raises sections for key functions

**Example Docstring:**
```python
def validate_group_id(group_id: str | None) -> bool:
    """
    Validate that a group_id contains only ASCII alphanumeric characters, dashes, and underscores.

    Args:
        group_id: The group_id to validate

    Returns:
        True if valid, False otherwise

    Raises:
        GroupIdValidationError: If group_id contains invalid characters
    """
```

## Function Design

**Size:** No strict line limit enforced, but functions aim for single responsibility
- Async functions handle database I/O and orchestration
- Pure functions handle data transformation

**Parameters:**
- Type hints required for all parameters
- Default values use sensible defaults (e.g., `Field(default_factory=...)` for Pydantic)
- Async coroutine parameters use `Coroutine` type hint

**Return Values:**
- All functions have type hints for return types
- Return type `None` explicitly annotated when returning nothing
- Complex returns often use tuples or custom data classes/Pydantic models

**Example:**
```python
async def hybrid_node_search(
    queries: list[str],
    embeddings: list[list[float]],
    driver: GraphDriver,
    search_filters: SearchFilters,
) -> list[EntityNode]:
    """Execute hybrid search combining fulltext and semantic search."""
```

## Module Design

**Exports:**
- Modules export primary classes and functions at module level
- No `__all__` enforced, but public APIs are clearly marked

**Barrel Files:**
- Not consistently used
- Imports are typically direct from source modules
- Example: Import directly from `graphiti_core.nodes` rather than through `graphiti_core.__init__`

## Pydantic Model Patterns

**BaseModel Usage:**
- All graph elements (nodes, edges) inherit from `pydantic.BaseModel`
- Models in `graphiti_core/nodes.py` and `graphiti_core/edges.py`

**Field Configuration:**
```python
from pydantic import BaseModel, ConfigDict, Field

class Node(BaseModel):
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(description='name of the node')
    group_id: str = Field(description='partition of the graph')
    created_at: datetime = Field(default_factory=lambda: utc_now())
    
    model_config = ConfigDict(validate_assignment=True)
```

**Field Validators:**
- Use `@field_validator` decorator from Pydantic v2
- Validators can call custom validation functions
- Applied to fields like `labels` to validate node label format

**Example:**
```python
from pydantic import field_validator

class Node(BaseModel):
    labels: list[str] = Field(default_factory=list)
    
    @field_validator('labels')
    @classmethod
    def validate_labels(cls, value: list[str]) -> list[str]:
        validate_node_labels(value)
        return value
```

**Custom Validators:**
- Validation logic extracted to standalone functions in `graphiti_core/helpers.py`
- Functions validate and raise custom exceptions if invalid
- Example validators: `validate_group_id()`, `validate_node_labels()`

## Type Hints

**Python Version:** 3.10+ required (set in `pyproject.toml`)

**Type Hint Patterns:**
- Modern union syntax: `str | None` instead of `Optional[str]`
- Generic list types: `list[str]`, `dict[str, Any]`
- `from typing import Any` for unknown types
- `from typing_extensions import LiteralString` for SQL/query strings
- `from numpy._typing import NDArray` for numpy arrays with shape hints

**Examples:**
```python
# Union with None
group_id: str | None

# Collections
labels: list[str]
embeddings: dict[str, float]

# Coroutines
coroutines: Coroutine

# Literal strings for SQL
query: LiteralString

# Numpy arrays
embedding: NDArray
```

---

*Convention analysis: 2026-04-17*
