"""Open every HTTP session the extension uses, and send the only requests that carry the ModelArk API key.

Every request is sent once. A failed request stops the run, since a paid request may have reached ModelArk before its
connection failed.
"""

from __future__ import annotations

import aiohttp
from yarl import URL
from http import HTTPStatus
from typing import TYPE_CHECKING
from .failures import read_failure
from ..types.parsing import parse_json
from contextlib import asynccontextmanager
from ..config.units import BYTES_PER_MEBIBYTE
from ..config.messages.media import DOWNLOAD_LIMIT
from ..types.errors import ErrorCode, BytePlusError
from ..config.byteplus import REPLY_BYTES, CONSOLE_URLS, ENDPOINT_URLS
from ..config.messages.run import (
    REQUEST_TIMEOUT,
    REPLY_UNREADABLE,
    REQUEST_UNCERTAIN,
    BYTEPLUS_UNREACHABLE,
    OUTPUT_DOWNLOAD_FAILED,
)

if TYPE_CHECKING:
    from ..types import Json
    from ..types.credentials import Credential
    from collections.abc import Mapping, AsyncGenerator
    from ..types.settings import Settings, Configuration


def _create_session(settings: Settings, credential: Credential | None) -> aiohttp.ClientSession:
    """Open one session for one request; the key goes only to ModelArk, never to BytePlus's storage hosts.

    Proxy settings from the environment and cookies are ignored, and every request refuses redirects, so neither the
    key nor a reply can pass through another host. aiohttp sends a GET again when its connection drops, and its only
    switch for that is private, so it is turned off here.
    """
    headers: dict[str, str] = {"Authorization": f"Bearer {credential.reveal()}"} if credential is not None else {}
    session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=settings.request_timeout_seconds),
        trust_env=False,
        cookie_jar=aiohttp.DummyCookieJar(),
        headers=headers,
    )
    setattr(session, "_retry_connection", False)  # noqa: B010 -- reason: aiohttp offers no public switch for its resend.
    return session


async def _read_body(response: aiohttp.ClientResponse, settings: Settings) -> bytes:
    """Read a reply or a file within the maximum download size."""
    maximum = settings.max_download_megabytes
    content = bytearray()
    async for chunk in response.content.iter_chunked(REPLY_BYTES["CHUNK"]):
        content.extend(chunk)
        if len(content) > maximum * BYTES_PER_MEBIBYTE:
            raise BytePlusError(ErrorCode.MEDIA, DOWNLOAD_LIMIT.format(maximum=maximum))
    return bytes(content)


async def _validate_reply(response: aiohttp.ClientResponse) -> None:
    """Refuse a reply that is not a success, reading at most a short error body."""
    if response.status < HTTPStatus.MULTIPLE_CHOICES:
        return
    body = await response.content.read(REPLY_BYTES["MAX_ERROR"])
    raise read_failure(response.status, body)


@asynccontextmanager
async def _validate_paid_request(settings: Settings) -> AsyncGenerator[None]:
    """Name what a failed paid request may have cost; nothing retries it."""
    try:
        yield
    except aiohttp.ClientConnectorError:
        # The connection failed before the request was sent, so nothing was billed.
        raise BytePlusError(ErrorCode.TRANSPORT, BYTEPLUS_UNREACHABLE) from None
    except aiohttp.ClientError:
        raise BytePlusError(ErrorCode.UNCERTAIN, REQUEST_UNCERTAIN.format(**CONSOLE_URLS)) from None
    except TimeoutError:
        seconds = settings.request_timeout_seconds
        raise BytePlusError(ErrorCode.TIMEOUT, REQUEST_TIMEOUT.format(seconds=seconds, **CONSOLE_URLS)) from None


@asynccontextmanager
async def _send_free_request(
    method: str, url: str | URL, settings: Settings, credential: Credential | None
) -> AsyncGenerator[aiohttp.ClientResponse]:
    """Send one request that bills nothing, once, and hand over its reply.

    A failure to connect or to read reads as BytePlus being out of reach, never as an uncertain charge, so the caller
    may send it again.
    """
    try:
        async with (
            _create_session(settings, credential) as session,
            session.request(method, url, allow_redirects=False) as response,
        ):
            yield response
    except (aiohttp.ClientError, TimeoutError):
        raise BytePlusError(ErrorCode.TRANSPORT, BYTEPLUS_UNREACHABLE) from None


def _parse_reply(content: bytes, code: ErrorCode) -> Json:
    """Read a JSON reply whose size the download limit already bounds.

    The reply came with a success status, so the code says what an unreadable one means: a paid request ran and may be
    billed, or a request that bills nothing failed.
    """
    try:
        text = content.decode("utf-8")
        return parse_json(text, max_bytes=len(content) + 1)
    except (UnicodeError, BytePlusError):
        raise BytePlusError(code, REPLY_UNREADABLE) from None


async def send_json(url: str, body: Mapping[str, Json], configuration: Configuration) -> Json:
    """Send one paid JSON request and return its parsed JSON reply."""
    async with (
        _validate_paid_request(configuration.settings),
        _create_session(configuration.settings, configuration.credential) as session,
        session.post(url, json=body, allow_redirects=False) as response,
    ):
        await _validate_reply(response)
        content = await _read_body(response, configuration.settings)
    return _parse_reply(content, ErrorCode.UNCERTAIN)


async def send_lookup(url: str, configuration: Configuration) -> Json:
    """Send one GET with the key that bills nothing, such as a task check, and return its parsed JSON reply."""
    settings = configuration.settings
    async with _send_free_request("GET", url, settings, configuration.credential) as response:
        await _validate_reply(response)
        content = await _read_body(response, settings)
    return _parse_reply(content, ErrorCode.TRANSPORT)


async def send_task_cancel(task_id: str, configuration: Configuration) -> None:
    """Cancel one queued task; ModelArk refuses to cancel a running one, and that refusal is raised.

    The task ID has already matched the task ID pattern, so it cannot change the address's path. A successful cancel
    has an empty body, which is not read.
    """
    url = f"{ENDPOINT_URLS['tasks']}/{task_id}"
    async with _send_free_request("DELETE", url, configuration.settings, configuration.credential) as response:
        await _validate_reply(response)


async def download_output(url: str, settings: Settings) -> bytes:
    """Download one output file from BytePlus's storage, once, without the key.

    The address carries its own signature, so it is sent byte for byte; a storage host's error body is not ModelArk's,
    so a failure names only its status. An address that is not https was never an output file, and the request that
    returned it ran.
    """
    if not url.startswith("https://"):
        raise BytePlusError(ErrorCode.UNCERTAIN, REPLY_UNREADABLE)
    async with _send_free_request("GET", URL(url, encoded=True), settings, None) as response:
        if response.status >= HTTPStatus.MULTIPLE_CHOICES:
            raise BytePlusError(ErrorCode.TRANSPORT, OUTPUT_DOWNLOAD_FAILED.format(status=response.status))
        return await _read_body(response, settings)


__all__ = ["download_output", "send_json", "send_lookup", "send_task_cancel"]
