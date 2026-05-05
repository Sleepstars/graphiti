"""
Copyright 2024, Zep Software, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
from collections.abc import Iterable

from openai import AsyncAzureOpenAI, AsyncOpenAI
from openai.types import EmbeddingModel

from .client import EmbedderClient, EmbedderConfig

DEFAULT_EMBEDDING_MODEL = 'text-embedding-3-small'

# DashScope's text-embedding-v3 caps batch size at 10. OpenAI accepts up to
# 2048. Default to 10 so DashScope-compatible deployments work out of the box;
# operators on first-party OpenAI can raise this via env to amortize round
# trips.
DEFAULT_OPENAI_BATCH_SIZE = int(os.environ.get('OPENAI_EMBEDDER_BATCH_SIZE', '10'))

# Models that support the native `dimensions` parameter for server-side
# truncation + re-normalization. Older models (text-embedding-ada-002,
# text-embedding-v1/v2) silently ignore or reject the param. DashScope's v3/v4
# accept it; first-party OpenAI text-embedding-3-* accept it.
_DIMENSIONS_AWARE_PREFIXES = (
    'text-embedding-3',
    'text-embedding-v3',
    'text-embedding-v4',
)


def _supports_dimensions_param(model: str | None) -> bool:
    if not model:
        return False
    name = str(model).lower()
    return any(name.startswith(prefix) for prefix in _DIMENSIONS_AWARE_PREFIXES)


class OpenAIEmbedderConfig(EmbedderConfig):
    embedding_model: EmbeddingModel | str = DEFAULT_EMBEDDING_MODEL
    api_key: str | None = None
    base_url: str | None = None
    batch_size: int = DEFAULT_OPENAI_BATCH_SIZE


class OpenAIEmbedder(EmbedderClient):
    """
    OpenAI Embedder Client

    This client supports both AsyncOpenAI and AsyncAzureOpenAI clients.
    """

    def __init__(
        self,
        config: OpenAIEmbedderConfig | None = None,
        client: AsyncOpenAI | AsyncAzureOpenAI | None = None,
    ):
        if config is None:
            config = OpenAIEmbedderConfig()
        self.config = config

        if client is not None:
            self.client = client
        else:
            self.client = AsyncOpenAI(api_key=config.api_key, base_url=config.base_url)

    def _embed_kwargs(self) -> dict:
        # Pass `dimensions` for models that support it so the server returns a
        # properly-truncated, re-normalized vector (matters for cosine
        # similarity quality once we slice). Models that don't support it get
        # client-side slicing only.
        if _supports_dimensions_param(self.config.embedding_model):
            return {'dimensions': self.config.embedding_dim}
        return {}

    async def create(
        self, input_data: str | list[str] | Iterable[int] | Iterable[Iterable[int]]
    ) -> list[float]:
        result = await self.client.embeddings.create(
            input=input_data,
            model=self.config.embedding_model,
            **self._embed_kwargs(),
        )
        return result.data[0].embedding[: self.config.embedding_dim]

    async def create_batch(self, input_data_list: list[str]) -> list[list[float]]:
        if not input_data_list:
            return []

        batch_size = max(1, self.config.batch_size)
        kwargs = self._embed_kwargs()
        embeddings: list[list[float]] = []
        for i in range(0, len(input_data_list), batch_size):
            chunk = input_data_list[i : i + batch_size]
            result = await self.client.embeddings.create(
                input=chunk, model=self.config.embedding_model, **kwargs
            )
            embeddings.extend(
                embedding.embedding[: self.config.embedding_dim] for embedding in result.data
            )
        return embeddings
