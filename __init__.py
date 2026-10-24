"""Load the BytePlus nodes and their local routes through ComfyUI's extension entry point."""

from __future__ import annotations

from typing import override
import asyncio

from comfy_api.latest import ComfyExtension, io

WEB_DIRECTORY = './web'


class Extension(ComfyExtension):
    """Create the shared stores, register the local routes, and list the nodes."""

    @override
    async def on_load(self) -> None:
        """Create the shared stores off the event loop, then register the local routes."""
        from .src.comfy.routes import register_routes  # noqa: PLC0415 # reason: ComfyUI sets up its modules first.
        from .src.comfy.runtime import create_runtime  # noqa: PLC0415 # reason: ComfyUI sets up its modules first.

        await asyncio.to_thread(create_runtime)
        register_routes()

    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        """Return the node classes in menu order."""
        from .src.nodes import NODE_TYPES  # noqa: PLC0415 # reason: The nodes import modules ComfyUI sets up first.

        return list(NODE_TYPES)


async def comfy_entrypoint() -> Extension:
    """Hand ComfyUI the extension."""
    return Extension()
