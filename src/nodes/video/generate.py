"""Make a video with any Seedance model, from a prompt, frames, references, or a draft, and keep it as references."""

from __future__ import annotations

import asyncio
import io as memory
from ..base import PaidNode
from functools import partial
from ...types.tasks import TaskRequest
from typing import cast, TYPE_CHECKING
from ...comfy.media import decode_image
from ...comfy.runtime import get_runtime
from ...types.videos import VideoRequest
from ...types.references import Reference
from comfy_api.latest import io, InputImpl
from datetime import UTC, datetime, timedelta
from comfy_execution.graph import ExecutionBlocker
from ...byteplus.videos.body import build_video_body
from ...byteplus.tasks.operation import TaskOperation
from ...config.generation.models import DEFAULT_MODELS
from ...byteplus.videos.modes import validate_video_request
from ...config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES
from ...comfy.execution import send_request, wait_for_task, wait_for_thread
from ...config.generation.inputs import INPUT_NAMES, MODEL_DEFAULT, MODEL_TOOLTIP
from ...config.generation.references import DRAFT_LIFETIME_SECONDS, OUTPUT_LIFETIME_SECONDS
from ..inputs import (
    REFERENCES_INPUT,
    read_image_socket,
    encode_audio_clips,
    IMAGE_SOCKET_TYPES,
    encode_sized_images,
    build_request_inputs,
)
from ...config.generation.videos import (
    RATIOS,
    DURATION,
    TASK_TYPES,
    RESOLUTIONS,
    AUDIO_VALUES,
    AUDIO_CHOICES,
    OUTPUT_FORMATS,
    POLL_INTERVAL_SECONDS,
)

if TYPE_CHECKING:
    import torch
    from comfy_api.latest import Input
    from ...types.options import Options
    from ...types.tasks import TaskResult
    from ...types.images import EncodedImage

# The video controls; a dropdown left at model default sends nothing, except resolution and duration, always sent.
_CONTROLS = (
    io.Int.Input(
        "duration",
        default=DURATION["DEFAULT"],
        min=DURATION["AUTO"],
        max=DURATION["MAX"],
        tooltip="Length in seconds. -1 lets the model choose; Seedance 2.5 may then make up to 30 seconds.",
    ),
    io.Combo.Input(
        "resolution",
        options=list(RESOLUTIONS["CHOICES"]),
        # RESOLUTIONS also holds the choices, so its values type as either; the default is text.
        default=cast("str", RESOLUTIONS["DEFAULT"]),
        tooltip="Always sent. Higher resolutions cost more, and each model takes only some; Model: Info lists them.",
    ),
    io.Combo.Input(
        "ratio",
        options=list(RATIOS),
        default=MODEL_DEFAULT,
        tooltip="The video's shape. Adaptive follows the first frame, the video being edited, or the prompt.",
    ),
    io.Combo.Input(
        "generate_audio",
        display_name="generate audio",
        options=list(AUDIO_CHOICES),
        default=MODEL_DEFAULT,
        tooltip="Whether the video has sound. Models that make sound make it unless this is false.",
    ),
    io.Combo.Input(
        "omni_reference_task_type",
        display_name="omni reference task type",
        options=list(TASK_TYPES),
        default=TASK_TYPES[0],
        tooltip=(
            "What Seedance 2.5 does with reference media: follow it, edit a reference video, or extend one. Auto "
            "lets the model decide."
        ),
    ),
    io.Boolean.Input(
        "draft",
        default=False,
        tooltip=(
            "Makes a quick 480p draft, on models that offer drafts. Connect its references to another Video: "
            "Generate to finish it."
        ),
    ),
    io.Boolean.Input(
        "camera_fixed",
        display_name="camera fixed",
        default=False,
        advanced=True,
        tooltip="Asks the model to keep the camera still, on models that take it.",
    ),
    io.Combo.Input(
        "output_format",
        display_name="output format",
        options=list(OUTPUT_FORMATS),
        default=MODEL_DEFAULT,
        advanced=True,
        tooltip="MP4 or MOV, on models that offer both. MOV keeps more color for editing; many players cannot play it.",
    ),
    io.Boolean.Input(
        "watermark",
        default=False,
        advanced=True,
        tooltip="Adds an AI Generated mark in the lower right corner.",
    ),
)

# The frames, each one image or references that hold one, and the local reference media.
_MEDIA = (
    io.MultiType.Input(
        "first_frame",
        types=list(IMAGE_SOCKET_TYPES),
        display_name="first frame",
        optional=True,
        tooltip=(
            "The image the video starts from: one image, or references that hold one image. References keep a "
            "ModelArk output trusted."
        ),
    ),
    io.MultiType.Input(
        "last_frame",
        types=list(IMAGE_SOCKET_TYPES),
        display_name="last frame",
        optional=True,
        tooltip="The image the video ends on, with a first frame.",
    ),
    io.Image.Input(
        "reference_image",
        display_name="reference image",
        optional=True,
        tooltip="Images the video follows: one, a batch, or a list. They come first, as Image 1, Image 2.",
    ),
    io.Audio.Input(
        "reference_audio",
        display_name="reference audio",
        optional=True,
        tooltip="Audio the video follows: one clip, a batch, or a list.",
    ),
)

# A frame socket's value: an encoded image, a reference, or nothing when the socket is not connected.
type _Frame = EncodedImage | Reference | None


def _encode_media(
    first_frame: list[object] | None,
    last_frame: list[object] | None,
    reference_image: list[torch.Tensor] | None,
    reference_audio: list[Input.Audio] | None,
) -> tuple[_Frame, _Frame, tuple[EncodedImage, ...], tuple[str, ...]]:
    """Read each connected frame socket, and encode the reference images and clips, in one worker thread."""
    first = read_image_socket("first frame", first_frame) if first_frame else None
    last = read_image_socket("last frame", last_frame) if last_frame else None
    return first, last, encode_sized_images(reference_image or ()), encode_audio_clips(reference_audio or ())


def build_video_outputs(result: TaskResult) -> io.NodeOutput:
    """Return the video, its decoded last frame, and their addresses as references, or the draft to finish.

    The task's creation time is when ModelArk accepted it, so a reference expires a little before its address does,
    never after. ComfyUI reads the video from memory, so no file is written.
    """
    created = datetime.fromtimestamp(result.created_at, UTC)
    video = result.outputs["video_url"]
    frame = result.outputs.get("last_frame_url")
    references: tuple[Reference, ...]
    if result.job.is_draft:
        expires_at = created + timedelta(seconds=DRAFT_LIFETIME_SECONDS)
        references = (Reference("draft", result.job.job_id, "output", expires_at),)
    else:
        expires_at = created + timedelta(seconds=OUTPUT_LIFETIME_SECONDS)
        references = (Reference("video", video.address, "output", expires_at),)
        if frame is not None:
            references += (Reference("image", frame.address, "output", expires_at),)
    last_frame: object = decode_image(frame.content)[0] if frame is not None else ExecutionBlocker(None)
    return io.NodeOutput(InputImpl.VideoFromFile(memory.BytesIO(video.content)), last_frame, references)


class VideoGenerate(PaidNode):
    """Create one video task, record it, wait for it, and return the video, its last frame, and their references."""

    list_inputs = frozenset({"first_frame", "last_frame", "reference_image", "reference_audio"})

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the model, the video controls, the frame and reference sockets, the seed, and the prompt."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Video: Generate",
            category=MENUS["VIDEO"],
            description="Make a video with any Seedance model, from a prompt, frames, references, or a draft.",
            inputs=[
                io.String.Input(INPUT_NAMES["MODEL"], default=DEFAULT_MODELS["videos"], tooltip=MODEL_TOOLTIP),
                *_CONTROLS,
                *_MEDIA,
                REFERENCES_INPUT,
                *build_request_inputs(has_seed=True),
                io.String.Input(
                    "prompt",
                    multiline=True,
                    default="",
                    placeholder="prompt",
                    tooltip=(
                        "What the video shows. Name media as Image 1, Video 1, Audio 1. Leave it empty to finish a "
                        "draft."
                    ),
                ),
            ],
            outputs=[
                io.Video.Output("video", display_name="video"),
                io.Image.Output("last_frame", display_name="last_frame"),
                io.Custom(SOCKET_TYPES["REFERENCES"]).Output("references", display_name="references"),
            ],
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    async def send(  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        prompt: str,
        model: str,
        seed: int,
        duration: int,
        resolution: str,
        ratio: str,
        generate_audio: str,
        omni_reference_task_type: str,
        draft: bool,
        camera_fixed: bool,
        output_format: str,
        watermark: bool,
        first_frame: list[object] | None = None,
        last_frame: list[object] | None = None,
        reference_image: list[torch.Tensor] | None = None,
        reference_audio: list[Input.Audio] | None = None,
        references: tuple[Reference, ...] | None = None,
        options: Options | None = None,
    ) -> io.NodeOutput:
        """Read the frames and encode the media inside the owned task, then create, record, and wait for the task."""

        async def send_encoded() -> io.NodeOutput:
            """Encode the media inside the owned task, then send the request."""
            first, last, images, clips = await wait_for_thread(
                lambda: _encode_media(first_frame, last_frame, reference_image, reference_audio)
            )
            # A dropdown left at model default sends nothing.
            request = VideoRequest(
                model_id=model.strip(),
                prompt=prompt,
                duration=duration,
                resolution=resolution,
                ratio=None if ratio == MODEL_DEFAULT else ratio,
                has_sound=AUDIO_VALUES.get(generate_audio),
                task_type=omni_reference_task_type,
                is_draft=draft,
                is_camera_fixed=camera_fixed,
                output_format=None if output_format == MODEL_DEFAULT else output_format,
                has_watermark=watermark,
                first_frame=first,
                last_frame=last,
                images=images,
                clips=clips,
                references=references or (),
                seed=seed,
                options=options,
            )
            task_request = TaskRequest(
                kind="videos",
                model_id=request.model_id,
                validate_request=partial(validate_video_request, request),
                build_body=partial(build_video_body, request),
                is_draft=request.is_draft,
                poll_seconds=POLL_INTERVAL_SECONDS,
            )
            operation = TaskOperation(task_request, get_runtime().jobs)
            return await send_request(operation, build_video_outputs, cls.hidden.unique_id)

        return await wait_for_task(asyncio.create_task(send_encoded()))


__all__ = ["VideoGenerate", "build_video_outputs"]
