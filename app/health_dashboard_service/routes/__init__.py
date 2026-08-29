"""Router auto-discovery: any module here exposing `router: APIRouter` is registered."""

import importlib
import pkgutil

from fastapi import APIRouter

__all__ = ["routers"]

routers: list[APIRouter] = []

for module_info in sorted(
    pkgutil.walk_packages(__path__, prefix=f"{__name__}."),
    key=lambda info: info.name,
):
    module = importlib.import_module(module_info.name)
    router = getattr(module, "router", None)

    if isinstance(router, APIRouter):
        routers.append(router)
