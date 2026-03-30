"""OpenAI-compatible LLM client that avoids json_schema response format.

Some providers (e.g. DashScope/Qwen) don't support the json_schema
response_format or hang indefinitely when it's used. This client always
uses json_object mode and relies on the prompt to enforce structure.
"""

import json
import logging
from typing import Any

import openai
from pydantic import BaseModel

from graphiti_core.cross_encoder.client import CrossEncoderClient
from graphiti_core.llm_client.config import DEFAULT_MAX_TOKENS, ModelSize
from graphiti_core.llm_client.errors import RateLimitError
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.prompts.models import Message

logger = logging.getLogger(__name__)


class CompatOpenAIClient(OpenAIGenericClient):
    """Drop-in replacement that always uses json_object response format."""

    async def _generate_response(
        self,
        messages: list[Message],
        response_model: type[BaseModel] | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        model_size: ModelSize = ModelSize.medium,
    ) -> dict[str, Any]:
        from openai.types.chat import ChatCompletionMessageParam

        openai_messages: list[ChatCompletionMessageParam] = []
        for m in messages:
            m.content = self._clean_input(m.content)
            if m.role == 'user':
                openai_messages.append({'role': 'user', 'content': m.content})
            elif m.role == 'system':
                openai_messages.append({'role': 'system', 'content': m.content})

        # DashScope requires "json" in the prompt to use json_object format.
        # Also inject schema hint so the model returns correctly named fields.
        schema_hint = ''
        if response_model is not None:
            schema = response_model.model_json_schema()
            schema_hint = (
                f'\n\nYou MUST respond with valid JSON matching this exact schema: {schema}'
            )
        json_instruction = (
            f'\nIMPORTANT: Respond ONLY with valid JSON.{schema_hint}'
        )
        if openai_messages and openai_messages[0]['role'] == 'system':
            openai_messages[0]['content'] += json_instruction  # type: ignore
        else:
            openai_messages.insert(0, {'role': 'system', 'content': json_instruction})

        try:
            response = await self.client.chat.completions.create(
                model=self.model or 'gpt-4.1-mini',
                messages=openai_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={'type': 'json_object'},
            )
            result = response.choices[0].message.content or ''
            return json.loads(result)
        except openai.RateLimitError as e:
            raise RateLimitError from e
        except Exception as e:
            logger.error(f'Error in generating LLM response: {e}')
            raise


class NoopCrossEncoder(CrossEncoderClient):
    """Pass-through cross encoder for providers that don't support logprobs."""

    async def rank(self, query: str, passages: list[str]) -> list[tuple[str, float]]:
        return [(p, 1.0) for p in passages]
