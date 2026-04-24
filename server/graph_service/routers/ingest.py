import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from functools import partial

from fastapi import APIRouter, FastAPI, status

logger = logging.getLogger(__name__)
from graphiti_core.errors import NodeNotFoundError  # type: ignore
from graphiti_core.nodes import EpisodeType, EpisodicNode  # type: ignore
from graphiti_core.utils.datetime_utils import utc_now  # type: ignore
from graphiti_core.utils.maintenance.graph_data_operations import clear_data  # type: ignore

from graph_service.dto import (
    AddEntityNodeRequest,
    AddEpisodeRequest,
    AddEpisodeResponse,
    AddMessagesRequest,
    Message,
    Result,
)
from graph_service.zep_graphiti import ZepGraphiti, ZepGraphitiDep


class AsyncWorker:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.task = None

    async def worker(self):
        while True:
            try:
                print(f'Got a job: (size of remaining queue: {self.queue.qsize()})')
                job = await self.queue.get()
                await job()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f'Ingest worker job failed: {e}')

    async def start(self):
        self.task = asyncio.create_task(self.worker())

    async def stop(self):
        if self.task:
            self.task.cancel()
            await self.task
        while not self.queue.empty():
            self.queue.get_nowait()


async_worker = AsyncWorker()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await async_worker.start()
    yield
    await async_worker.stop()


router = APIRouter(lifespan=lifespan)


async def _ensure_episodic_node(
    graphiti: ZepGraphiti,
    *,
    uuid: str | None,
    group_id: str,
    name: str,
    episode_body: str,
    source: EpisodeType,
    source_description: str,
    reference_time: datetime,
) -> None:
    """Pre-create an ``EpisodicNode`` when the caller supplied its own uuid.

    ``graphiti_core>=0.5`` reinterprets the ``uuid=`` kwarg on ``add_episode``
    as a lookup key (``EpisodicNode.get_by_uuid``) instead of an override for
    the newly-created node's uuid. Callers that want to control the episode's
    uuid (e.g. to correlate with their own store for later ``DELETE
    /episode/{uuid}`` calls) must therefore persist the node first; the
    downstream ``_process_episode_data`` upsert will then update it in place.

    For drivers that partition the graph by ``group_id`` (FalkorDB stores each
    group in its own graph DB), we must target the same partition
    ``add_episode`` will later clone to, otherwise our save lands in the
    default DB and add_episode's get_by_uuid misses it. Mirror the same
    clone-on-mismatch pattern used in ``Graphiti.add_episode``.

    When ``uuid`` is ``None`` this is a no-op — ``add_episode`` will generate
    and persist a fresh uuid itself.
    """
    if uuid is None:
        return

    driver = graphiti.driver
    if group_id and group_id != getattr(driver, '_database', group_id):
        driver = driver.clone(database=group_id)

    try:
        await EpisodicNode.get_by_uuid(driver, uuid)
        # Already persisted (likely a retry); graphiti.add_episode will fetch it.
        return
    except NodeNotFoundError:
        pass

    now = utc_now()
    episode = EpisodicNode(
        uuid=uuid,
        name=name,
        group_id=group_id,
        labels=[],
        source=source,
        content=episode_body,
        source_description=source_description,
        created_at=now,
        valid_at=reference_time,
    )
    await episode.save(driver)


@router.post('/messages', status_code=status.HTTP_202_ACCEPTED)
async def add_messages(
    request: AddMessagesRequest,
    graphiti: ZepGraphitiDep,
):
    async def add_messages_task(m: Message):
        episode_body = f'{m.role or ""}({m.role_type}): {m.content}'
        await _ensure_episodic_node(
            graphiti,
            uuid=m.uuid,
            group_id=request.group_id,
            name=m.name,
            episode_body=episode_body,
            source=EpisodeType.message,
            source_description=m.source_description,
            reference_time=m.timestamp,
        )
        await graphiti.add_episode(
            uuid=m.uuid,
            group_id=request.group_id,
            name=m.name,
            episode_body=episode_body,
            reference_time=m.timestamp,
            source=EpisodeType.message,
            source_description=m.source_description,
        )

    for m in request.messages:
        await async_worker.queue.put(partial(add_messages_task, m))

    return Result(message='Messages added to processing queue', success=True)


@router.post('/entity-node', status_code=status.HTTP_201_CREATED)
async def add_entity_node(
    request: AddEntityNodeRequest,
    graphiti: ZepGraphitiDep,
):
    node = await graphiti.save_entity_node(
        uuid=request.uuid,
        group_id=request.group_id,
        name=request.name,
        summary=request.summary,
    )
    return node


@router.post('/episodes', status_code=status.HTTP_201_CREATED)
async def add_episode(
    request: AddEpisodeRequest,
    graphiti: ZepGraphitiDep,
):
    reference_time = (
        request.reference_time.replace(tzinfo=timezone.utc)
        if request.reference_time.tzinfo is None
        else request.reference_time.astimezone(timezone.utc)
    )
    await _ensure_episodic_node(
        graphiti,
        uuid=request.uuid,
        group_id=request.group_id,
        name=request.name,
        episode_body=request.episode_body,
        source=EpisodeType.message,
        source_description=request.source_description,
        reference_time=reference_time,
    )
    result = await graphiti.add_episode(
        uuid=request.uuid,
        group_id=request.group_id,
        name=request.name,
        episode_body=request.episode_body,
        reference_time=reference_time,
        source=EpisodeType.message,
        source_description=request.source_description,
    )
    return AddEpisodeResponse(uuid=result.episode.uuid)


@router.delete('/entity-edge/{uuid}', status_code=status.HTTP_200_OK)
async def delete_entity_edge(uuid: str, graphiti: ZepGraphitiDep):
    await graphiti.delete_entity_edge(uuid)
    return Result(message='Entity Edge deleted', success=True)


@router.delete('/group/{group_id}', status_code=status.HTTP_200_OK)
async def delete_group(group_id: str, graphiti: ZepGraphitiDep):
    await graphiti.delete_group(group_id)
    return Result(message='Group deleted', success=True)


@router.delete('/episode/{uuid}', status_code=status.HTTP_200_OK)
async def delete_episode(uuid: str, graphiti: ZepGraphitiDep):
    await graphiti.delete_episodic_node(uuid)
    return Result(message='Episode deleted', success=True)


@router.delete('/episodes/{uuid}', status_code=status.HTTP_200_OK)
async def delete_episode_plural(uuid: str, graphiti: ZepGraphitiDep):
    await graphiti.delete_episodic_node(uuid)
    return Result(message='Episode deleted', success=True)


@router.post('/clear', status_code=status.HTTP_200_OK)
async def clear(
    graphiti: ZepGraphitiDep,
):
    await clear_data(graphiti.driver)
    await graphiti.build_indices_and_constraints()
    return Result(message='Graph cleared', success=True)
