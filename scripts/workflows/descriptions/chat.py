"""The chat workflows: write a product listing from a photo and a spec sheet, and summarize a voice note."""

from __future__ import annotations

import json
from scripts.nodes.host import HostNode
from src.config.namespace import NODE_PREFIX
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.page.config import STAGE_COLOUR, TEXT_PREVIEW, IMAGE_PREVIEW

ASK = f"{NODE_PREFIX}ChatAsk"
MINI = "seed-2-0-mini-260428"
DEEPSEEK = "deepseek-v4-flash-ga-260731"
LISTING_SCHEMA = json.dumps(
    {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "bullets": {"type": "array", "items": {"type": "string"}},
            "description": {"type": "string"},
        },
        "required": ["title", "bullets", "description"],
        "additionalProperties": False,
    },
    indent=2,
)
LISTING_PROMPT = (
    "Write a marketplace listing for this product from the photo and the spec sheet. Use only facts you can see in "
    "the photo or read in the spec sheet. Keep the title under 80 characters, write five bullet points, and keep the "
    "description under 60 words."
)
ACTIONS_PROMPT = (
    "List every action item in the voice note as a checklist, each with who does it and by when if the note says. "
    "Then sum up the note in two sentences."
)
LISTING_TEXTS = WORKFLOW_TEXTS["chat-01-write-a-product-listing"]
VOICE_TEXTS = WORKFLOW_TEXTS["chat-02-summarize-a-voice-note"]

PHOTO = Subgraph(
    name=SHARED_TEXTS["photo"],
    nodes=(
        Node("draw", f"{NODE_PREFIX}ImageGenerate", {"aspect_ratio": "1:1"}, is_paid=True),
        Node("look", HostNode.PREVIEW_IMAGE),
    ),
    links=(("draw.images", "look.images"),),
    columns=(("draw",), ("look",)),
    inputs=(("product", "draw.prompt"),),
    outputs=(("image", "draw.images"),),
    description=LISTING_TEXTS["photo_description"],
    previews=(("look", IMAGE_PREVIEW),),
)

WRITE = Subgraph(
    name=SHARED_TEXTS["write"],
    nodes=(
        Node(
            "ask",
            ASK,
            {"thinking": "off", "answer_schema": LISTING_SCHEMA, "prompt": LISTING_PROMPT},
            is_paid=True,
        ),
        Node("save", HostNode.SAVE_TEXT, {"filename_prefix": "text/byteplus/product-listing", "format": "json"}),
    ),
    links=(("ask.text", "save.text"),),
    columns=(("ask",), ("save",)),
    inputs=(("image", "ask.images"), ("documents", "ask.documents")),
    description=LISTING_TEXTS["write_description"],
    previews=(("save", TEXT_PREVIEW),),
)

WRITE_LISTING = Workflow(
    slug="chat-01-write-a-product-listing",
    nodes=(
        Node(
            "product",
            HostNode.TEXT_BLOCK,
            {
                "value": (
                    "A stainless steel insulated water bottle, 750 ml, matte sage green with a bamboo lid, on a plain "
                    "white background, soft studio light"
                )
            },
            title=SHARED_TEXTS["product"],
        ),
        Node("spec", f"{NODE_PREFIX}ChatAttachDocument", {"file": ""}),
        Node("photo", PHOTO.name),
        Node("write", WRITE.name),
    ),
    links=(
        ("product.STRING", "photo.product"),
        ("photo.image", "write.image"),
        ("spec.documents", "write.documents"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("product",), ("spec",)), note=LISTING_TEXTS["input"]),),
        (Group(SHARED_TEXTS["photo"], (("photo",),), STAGE_COLOUR, LISTING_TEXTS["photo"]),),
        (Group(SHARED_TEXTS["write"], (("write",),), STAGE_COLOUR, LISTING_TEXTS["write"]),),
    ),
    subgraphs=(PHOTO, WRITE),
)

TRANSCRIBE = Subgraph(
    name=SHARED_TEXTS["transcribe"],
    nodes=(
        Node(
            "ask",
            ASK,
            {
                "model": MINI,
                "thinking": "off",
                "prompt": "Transcribe this voice note word for word. Write only what is said.",
            },
            is_paid=True,
        ),
        Node("save", HostNode.SAVE_TEXT, {"filename_prefix": "text/byteplus/voice-note-transcript"}),
    ),
    links=(("ask.text", "save.text"),),
    columns=(("ask",), ("save",)),
    inputs=(("audio", "ask.audio"),),
    outputs=(("conversation", "ask.conversation"),),
    description=VOICE_TEXTS["transcribe_description"],
    previews=(("save", TEXT_PREVIEW),),
)

ACTIONS = Subgraph(
    name=SHARED_TEXTS["actions"],
    nodes=(
        Node("ask", ASK, {"model": DEEPSEEK, "prompt": ACTIONS_PROMPT}, is_paid=True),
        Node("save", HostNode.SAVE_TEXT, {"filename_prefix": "text/byteplus/voice-note-actions", "format": "md"}),
    ),
    links=(("ask.text", "save.text"),),
    columns=(("ask",), ("save",)),
    inputs=(("conversation", "ask.conversation"), ("options", "ask.options")),
    description=VOICE_TEXTS["actions_description"],
    previews=(("save", TEXT_PREVIEW),),
)

SUMMARIZE_VOICE_NOTE = Workflow(
    slug="chat-02-summarize-a-voice-note",
    nodes=(
        Node("voice_note", HostNode.AUDIO, {"audio": ""}, title=SHARED_TEXTS["voice_note"]),
        Node("transcribe", TRANSCRIBE.name),
        Node("flex", f"{NODE_PREFIX}RequestOptions", {"tier": "flex"}),
        Node("actions", ACTIONS.name),
    ),
    links=(
        ("voice_note.AUDIO", "transcribe.audio"),
        ("transcribe.conversation", "actions.conversation"),
        ("flex.options", "actions.options"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("voice_note",),), note=VOICE_TEXTS["input"]),),
        (Group(SHARED_TEXTS["transcribe"], (("transcribe",),), STAGE_COLOUR, VOICE_TEXTS["transcribe"]),),
        (Group(SHARED_TEXTS["actions"], (("flex",), ("actions",)), STAGE_COLOUR, VOICE_TEXTS["actions"]),),
    ),
    subgraphs=(TRANSCRIBE, ACTIONS),
)

CHAT_WORKFLOWS = (WRITE_LISTING, SUMMARIZE_VOICE_NOTE)

__all__ = ["CHAT_WORKFLOWS"]
