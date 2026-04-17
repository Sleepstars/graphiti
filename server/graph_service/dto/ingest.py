from datetime import datetime

from graphiti_core.utils.datetime_utils import utc_now
from pydantic import BaseModel, Field

from graph_service.dto.common import Message


class AddMessagesRequest(BaseModel):
    group_id: str = Field(..., description='The group id of the messages to add')
    messages: list[Message] = Field(..., description='The messages to add')


class AddEntityNodeRequest(BaseModel):
    uuid: str = Field(..., description='The uuid of the node to add')
    group_id: str = Field(..., description='The group id of the node to add')
    name: str = Field(..., description='The name of the node to add')
    summary: str = Field(default='', description='The summary of the node to add')


class AddEpisodeRequest(BaseModel):
    group_id: str = Field(..., description='The group id of the episode')
    name: str = Field(..., description='The name of the episode')
    episode_body: str = Field(..., description='The content of the episode')
    source_description: str = Field(default='', description='The source description of the episode')
    reference_time: datetime = Field(
        default_factory=utc_now, description='The reference time of the episode'
    )
    uuid: str | None = Field(default=None, description='Optional episode uuid')


class AddEpisodeResponse(BaseModel):
    uuid: str = Field(..., description='The uuid of the created episode')
