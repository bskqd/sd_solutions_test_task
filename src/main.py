from typing import Callable

from fastapi import FastAPI

from api.handlers import router as handlers_router
from config import Config
from dependencies import DependenciesOverrides


def create_application(dependency_overrides_factory: Callable, config: Config) -> FastAPI:
    application = FastAPI()

    application.dependency_overrides = dependency_overrides_factory(config)

    application.include_router(handlers_router, prefix="/api/v1")

    return application


def fastapi_dependency_overrides_factory(config: Config) -> dict:
    dependencies_overrides = DependenciesOverrides(config)
    return {
        **dependencies_overrides.override_dependencies(),
    }


app = create_application(fastapi_dependency_overrides_factory, Config())
