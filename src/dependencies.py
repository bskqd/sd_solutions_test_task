import functools
from typing import Callable

import miniopy_async
import redis.asyncio as redis
from fastapi import Depends
from openai import AsyncOpenAI

from infrastructure.agents import GenerateQuestionsAgent, ResponseEvaluationAgent, ValidationAgent
from config import Config
from infrastructure.files_storage import FilesStorage
from infrastructure.shared_context import SharedContext
from services import GenerateQuestionsService, EvaluateResponsesService, ValidationService


class Stub:
    def __init__(self, dependency: Callable, **kwargs):
        self._dependency = dependency
        self._kwargs = kwargs

    def __call__(self):
        raise NotImplementedError

    def __eq__(self, other) -> bool:
        if isinstance(other, Stub):
            return self._dependency == other._dependency and self._kwargs == other._kwargs
        if not self._kwargs:
            return self._dependency == other
        return False

    def __hash__(self):
        if not self._kwargs:
            return hash(self._dependency)
        serial = (self._dependency, *self._kwargs.items(),)
        return hash(serial)


class DependenciesOverrides:
    def __init__(self, config: Config):
        self.config = config
        self.db_sessionmaker = None

    def override_dependencies(self) -> dict:
        return {
            Config: self.get_config,
            redis.Redis: self.get_redis_shared_context_connection,
            miniopy_async.Minio: self.get_minio_client,
            FilesStorage: self.get_files_storage,
            AsyncOpenAI: self.get_openai_client,
            GenerateQuestionsAgent: self.get_generate_questions_agent,
            ResponseEvaluationAgent: self.get_response_evaluation_agent,
            ValidationAgent: self.get_validation_agent,
            SharedContext: self.get_shared_context,
            GenerateQuestionsService: self.get_questions_generation_service,
            EvaluateResponsesService: self.get_responses_evaluation_service,
            ValidationService: self.get_validation_service,
        }

    def get_config(self):
        return self.config

    @functools.lru_cache(maxsize=1)
    def get_redis_shared_context_connection(self):
        return redis.Redis.from_url(self.config.REDIS_HOST_URL, db=self.config.REDIS_SHARED_CONTEXT_DB)

    @functools.lru_cache(maxsize=1)
    def get_minio_client(self):
        return miniopy_async.Minio(
            endpoint=self.config.MINIO_URL,
            secure=self.config.MINIO_SECURE,
            access_key=self.config.MINIO_ACCESS_KEY,
            secret_key=self.config.MINIO_SECRET_KEY,
        )

    @functools.lru_cache(maxsize=1)
    def get_files_storage(
            self,
            config: Config = Depends(Stub(Config)),
            minio_client: miniopy_async.Minio = Depends(Stub(miniopy_async.Minio)),
    ):
        return FilesStorage(config, minio_client)

    @functools.lru_cache(maxsize=1)
    def get_openai_client(self):
        return AsyncOpenAI(api_key=self.config.OPENAI_API_KEY)

    @functools.lru_cache(maxsize=1)
    def get_generate_questions_agent(self, client: AsyncOpenAI = Depends(Stub(AsyncOpenAI))):
        return GenerateQuestionsAgent(client)

    @functools.lru_cache(maxsize=1)
    def get_response_evaluation_agent(self, client: AsyncOpenAI = Depends(Stub(AsyncOpenAI))):
        return ResponseEvaluationAgent(client)

    @functools.lru_cache(maxsize=1)
    def get_validation_agent(self, client: AsyncOpenAI = Depends(Stub(AsyncOpenAI))):
        return ValidationAgent(client)

    def get_shared_context(self, redis_connection: redis.Redis = Depends(Stub(redis.Redis))):
        return SharedContext(redis_connection)

    def get_questions_generation_service(
            self,
            shared_context: SharedContext = Depends(Stub(SharedContext)),
            agent: GenerateQuestionsAgent = Depends(Stub(GenerateQuestionsAgent)),
    ):
        return GenerateQuestionsService(shared_context, agent)

    def get_responses_evaluation_service(
            self,
            shared_context: SharedContext = Depends(Stub(SharedContext)),
            agent: ResponseEvaluationAgent = Depends(Stub(ResponseEvaluationAgent)),
    ):
        return EvaluateResponsesService(shared_context, agent)

    def get_validation_service(
            self,
            config: Config = Depends(Stub(Config)),
            shared_context: SharedContext = Depends(Stub(SharedContext)),
            agent: ValidationAgent = Depends(Stub(ValidationAgent)),
            files_storage_client: FilesStorage = Depends(Stub(FilesStorage))
    ):
        return ValidationService(config, shared_context, agent, files_storage_client)
