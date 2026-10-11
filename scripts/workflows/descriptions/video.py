"""The video workflows: animate a character, continue a shot, cast a preset character, finish a draft, and recover."""

from __future__ import annotations

from scripts.nodes.host import HostNode
from src.config.namespace import NODE_PREFIX
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.page.config import STAGE_COLOUR, IMAGE_PREVIEW, VIDEO_PREVIEW

GENERATE = f"{NODE_PREFIX}VideoGenerate"
SEEDANCE_25 = "dreamina-seedance-2-5-260628"
SCENE_PROMPT = 'She smiles, waves, and says: "Welcome to the night market." Handheld camera, warm light.'
ANIMATE_TEXTS = WORKFLOW_TEXTS["video-01-animate-a-character"]
CONTINUE_TEXTS = WORKFLOW_TEXTS["video-02-continue-a-shot"]
CAST_TEXTS = WORKFLOW_TEXTS["video-03-cast-a-preset-character"]
DRAFT_TEXTS = WORKFLOW_TEXTS["video-04-draft-then-finish"]
RECOVER_TEXTS = WORKFLOW_TEXTS["video-05-recover-a-video"]

DESIGN = Subgraph(
    name=SHARED_TEXTS["design"],
    nodes=(
        Node("draw", f"{NODE_PREFIX}ImageGenerate", {"size": "2048x1152"}, is_paid=True),
        Node("look", HostNode.PREVIEW_IMAGE),
    ),
    links=(("draw.images", "look.images"),),
    columns=(("draw",), ("look",)),
    inputs=(("character", "draw.prompt"),),
    outputs=(("references", "draw.references"),),
    description=ANIMATE_TEXTS["design_description"],
    previews=(("look", IMAGE_PREVIEW),),
)

ANIMATE = Subgraph(
    name=SHARED_TEXTS["animate"],
    nodes=(
        Node("video", GENERATE, {"resolution": "480p"}, is_paid=True),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/byteplus/character"}),
    ),
    links=(("video.video", "save.video"),),
    columns=(("video",), ("save",)),
    inputs=(("frame", "video.first_frame"), ("scene", "video.prompt")),
    description=ANIMATE_TEXTS["animate_description"],
    previews=(("save", VIDEO_PREVIEW),),
)

ANIMATE_CHARACTER = Workflow(
    slug="video-01-animate-a-character",
    nodes=(
        Node(
            "character",
            HostNode.TEXT_BLOCK,
            {
                "value": (
                    "Waist-up portrait of an original character: a street-food guide in her thirties with short black "
                    "hair and a red apron, standing in a lantern-lit night market, looking at the camera, "
                    "photorealistic."
                )
            },
            title=SHARED_TEXTS["character"],
        ),
        Node("scene", HostNode.TEXT_BLOCK, {"value": SCENE_PROMPT}, title=SHARED_TEXTS["scene"]),
        Node("design", DESIGN.name),
        Node("animate", ANIMATE.name),
    ),
    links=(
        ("character.STRING", "design.character"),
        ("design.references", "animate.frame"),
        ("scene.STRING", "animate.scene"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("character", "scene"),), note=ANIMATE_TEXTS["input"]),),
        (Group(SHARED_TEXTS["design"], (("design",),), STAGE_COLOUR, ANIMATE_TEXTS["design"]),),
        (Group(SHARED_TEXTS["animate"], (("animate",),), STAGE_COLOUR, ANIMATE_TEXTS["animate"]),),
    ),
    subgraphs=(DESIGN, ANIMATE),
)

FIRST_SHOT = Subgraph(
    name=SHARED_TEXTS["shot_1"],
    nodes=(
        Node("video", GENERATE, {"resolution": "480p"}, is_paid=True),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/byteplus/shot-1"}),
    ),
    links=(("video.video", "save.video"),),
    columns=(("video",), ("save",)),
    inputs=(("prompt", "video.prompt"),),
    outputs=(("references", "video.references"), ("video", "video.video")),
    description=CONTINUE_TEXTS["shot_1_description"],
    previews=(("save", VIDEO_PREVIEW),),
)

NEXT_SHOT = Subgraph(
    name=SHARED_TEXTS["shot_2"],
    nodes=(
        Node("video", GENERATE, {"resolution": "480p"}, is_paid=True),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/byteplus/shot-2"}),
    ),
    links=(("video.video", "save.video"),),
    columns=(("video",), ("save",)),
    inputs=(("frame", "video.first_frame"), ("prompt", "video.prompt")),
    outputs=(("video", "video.video"),),
    description=CONTINUE_TEXTS["shot_2_description"],
    previews=(("save", VIDEO_PREVIEW),),
)

JOIN = Subgraph(
    name=SHARED_TEXTS["join"],
    nodes=(
        Node("join", HostNode.JOIN_VIDEOS),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/byteplus/continued"}),
    ),
    links=(("join.VIDEO", "save.video"),),
    columns=(("join",), ("save",)),
    inputs=(("first", "join.videos.video0"), ("second", "join.videos.video1")),
    description=CONTINUE_TEXTS["join_description"],
    previews=(("save", VIDEO_PREVIEW),),
)

CONTINUE_SHOT = Workflow(
    slug="video-02-continue-a-shot",
    nodes=(
        Node(
            "opening",
            HostNode.TEXT_BLOCK,
            {"value": "A paper boat sails down a rainy city gutter toward a storm drain; low camera following it."},
            title=SHARED_TEXTS["opening"],
        ),
        Node(
            "next",
            HostNode.TEXT_BLOCK,
            {"value": "The paper boat drifts out of a tunnel onto a calm, sunlit lake; the camera rises slowly."},
            title=SHARED_TEXTS["next"],
        ),
        Node("shot_1", FIRST_SHOT.name),
        Node("shot_2", NEXT_SHOT.name),
        Node("join", JOIN.name),
    ),
    links=(
        ("opening.STRING", "shot_1.prompt"),
        ("shot_1.references", "shot_2.frame"),
        ("next.STRING", "shot_2.prompt"),
        ("shot_1.video", "join.first"),
        ("shot_2.video", "join.second"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("opening", "next"),), note=CONTINUE_TEXTS["input"]),),
        (Group(SHARED_TEXTS["shot_1"], (("shot_1",),), STAGE_COLOUR, CONTINUE_TEXTS["shot_1"]),),
        (Group(SHARED_TEXTS["shot_2"], (("shot_2",),), STAGE_COLOUR, CONTINUE_TEXTS["shot_2"]),),
        (Group(SHARED_TEXTS["join"], (("join",),), STAGE_COLOUR, CONTINUE_TEXTS["join"]),),
    ),
    subgraphs=(FIRST_SHOT, NEXT_SHOT, JOIN),
)

DRAW = Subgraph(
    name=SHARED_TEXTS["draw"],
    nodes=(
        Node("draw", f"{NODE_PREFIX}ImageGenerate", is_paid=True),
        Node("look", HostNode.PREVIEW_IMAGE),
    ),
    links=(("draw.images", "look.images"),),
    columns=(("draw",), ("look",)),
    inputs=(("product", "draw.prompt"),),
    outputs=(("references", "draw.references"),),
    description=CAST_TEXTS["draw_description"],
    previews=(("look", IMAGE_PREVIEW),),
)

FILM = Subgraph(
    name=SHARED_TEXTS["film"],
    nodes=(
        Node("video", GENERATE, is_paid=True),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/byteplus/preset-character"}),
    ),
    links=(("video.video", "save.video"),),
    columns=(("video",), ("save",)),
    inputs=(("references", "video.references"), ("scene", "video.prompt")),
    description=CAST_TEXTS["film_description"],
    previews=(("save", VIDEO_PREVIEW),),
)

CAST_CHARACTER = Workflow(
    slug="video-03-cast-a-preset-character",
    nodes=(
        Node(
            "product",
            HostNode.TEXT_BLOCK,
            {"value": "A glass jar of face cream with a gold lid on a plain white background, soft studio light"},
            title=SHARED_TEXTS["product"],
        ),
        Node(
            "scene",
            HostNode.TEXT_BLOCK,
            {
                "value": (
                    "The person in Image 2 holds up the jar from Image 1 and smiles at the camera. Soft daylight, slow "
                    "push-in."
                )
            },
            title=SHARED_TEXTS["scene"],
        ),
        Node("draw", DRAW.name),
        Node("cast", f"{NODE_PREFIX}ReferenceAdd"),
        Node("film", FILM.name),
    ),
    links=(
        ("product.STRING", "draw.product"),
        ("draw.references", "cast.references"),
        ("cast.references", "film.references"),
        ("scene.STRING", "film.scene"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("product", "scene"),), note=CAST_TEXTS["input"]),),
        (Group(SHARED_TEXTS["product"], (("draw",),), STAGE_COLOUR, CAST_TEXTS["product"]),),
        (Group(SHARED_TEXTS["character"], (("cast",),), STAGE_COLOUR, CAST_TEXTS["character"]),),
        (Group(SHARED_TEXTS["video"], (("film",),), STAGE_COLOUR, CAST_TEXTS["video"]),),
    ),
    subgraphs=(DRAW, FILM),
)

DRAFT = Subgraph(
    name=SHARED_TEXTS["draft"],
    nodes=(
        Node(
            "video",
            GENERATE,
            {"model": SEEDANCE_25, "duration": 4, "resolution": "480p", "draft": True},
            is_paid=True,
        ),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/byteplus/draft"}),
    ),
    links=(("video.video", "save.video"),),
    columns=(("video",), ("save",)),
    inputs=(("prompt", "video.prompt"),),
    outputs=(("references", "video.references"),),
    description=DRAFT_TEXTS["draft_description"],
    previews=(("save", VIDEO_PREVIEW),),
)

FINISH = Subgraph(
    name=SHARED_TEXTS["finish"],
    nodes=(
        Node("video", GENERATE, {"model": SEEDANCE_25, "resolution": "1080p"}, is_paid=True),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/byteplus/final"}),
    ),
    links=(("video.video", "save.video"),),
    columns=(("video",), ("save",)),
    inputs=(("references", "video.references"),),
    description=DRAFT_TEXTS["finish_description"],
    previews=(("save", VIDEO_PREVIEW),),
)

FINISH_DRAFT = Workflow(
    slug="video-04-draft-then-finish",
    nodes=(
        Node(
            "prompt",
            HostNode.TEXT_BLOCK,
            {
                "value": (
                    "A red kite climbs over green hills on a windy afternoon, its tail ribbons fluttering; the camera "
                    "tilts up to follow it into the clouds."
                )
            },
            title=SHARED_TEXTS["prompt"],
        ),
        Node("draft", DRAFT.name),
        Node("finish", FINISH.name, is_bypassed=True),
    ),
    links=(("prompt.STRING", "draft.prompt"), ("draft.references", "finish.references")),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("prompt",),), note=DRAFT_TEXTS["input"]),),
        (Group(SHARED_TEXTS["draft"], (("draft",),), STAGE_COLOUR, DRAFT_TEXTS["draft"]),),
        (Group(SHARED_TEXTS["finish"], (("finish",),), STAGE_COLOUR, DRAFT_TEXTS["finish"]),),
    ),
    subgraphs=(DRAFT, FINISH),
)

RECOVER_VIDEO = Workflow(
    slug="video-05-recover-a-video",
    nodes=(
        Node("download", f"{NODE_PREFIX}VideoDownload", {"job": ""}),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/byteplus/recovered"}),
        Node("last_frame", HostNode.PREVIEW_IMAGE, title=SHARED_TEXTS["last_frame"]),
    ),
    links=(("download.video", "save.video"), ("download.last_frame", "last_frame.images")),
    stacks=(
        (
            Group(
                SHARED_TEXTS["recover"],
                (("download",), ("save", "last_frame")),
                STAGE_COLOUR,
                RECOVER_TEXTS["recover"],
            ),
        ),
    ),
)

VIDEO_WORKFLOWS = (ANIMATE_CHARACTER, CONTINUE_SHOT, CAST_CHARACTER, FINISH_DRAFT, RECOVER_VIDEO)

__all__ = ["VIDEO_WORKFLOWS"]
