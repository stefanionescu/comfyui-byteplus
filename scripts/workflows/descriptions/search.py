"""The search workflow: draw hero image options from a brief, score each against it, and save the best."""

from __future__ import annotations

from scripts.nodes.host import HostNode
from src.config.namespace import NODE_PREFIX
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.config import STAGE_COLOUR, IMAGE_PREVIEW
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.descriptions.nodes import SEEDREAM_4, IMAGE_GENERATE

# One similarity as JSON writes it: a signed number, with a fraction or an exponent when it has one.
SCORE = r"(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)"
# The brief's similarity to itself, then four option scores. Choose pads the list with four -2 scores, so it always
# holds at least five numbers, even when Seedream made fewer images.
SCORES_PATTERN = r"[^-\d]+".join([SCORE] * 5)
HERO_TEXTS = WORKFLOW_TEXTS["search-01-choose-a-hero-image"]

DRAW = Subgraph(
    name=SHARED_TEXTS["options"],
    nodes=(
        Node(
            "prompt",
            HostNode.FORMAT,
            {
                "f_string": (
                    "Generate 4 different hero photos for an online shop's home page, each with a new camera angle "
                    "and composition: {a}"
                )
            },
        ),
        Node(
            "draw",
            IMAGE_GENERATE,
            {"model": SEEDREAM_4, "size": "2848x1600", "max_images": 4},
            is_paid=True,
        ),
        Node("look", HostNode.PREVIEW_IMAGE),
    ),
    links=(("prompt.STRING", "draw.prompt"), ("draw.images", "look.images")),
    columns=(("prompt",), ("draw",), ("look",)),
    inputs=(("brief", "prompt.values.a"),),
    outputs=(("images", "draw.images"),),
    description=HERO_TEXTS["draw_description"],
    previews=(("look", IMAGE_PREVIEW),),
)

EMBED = Subgraph(
    name=SHARED_TEXTS["score"],
    nodes=(
        Node(
            "embed",
            f"{NODE_PREFIX}SearchEmbed",
            {
                "instructions": (
                    "Target_modality: text/image.\nInstruction:Find the image that best matches this product "
                    "description\nQuery:"
                )
            },
            is_paid=True,
        ),
    ),
    links=(),
    columns=(("embed",),),
    inputs=(("brief", "embed.texts"), ("images", "embed.images")),
    outputs=(("similarities", "embed.similarities"),),
    description=HERO_TEXTS["score_description"],
)

CHOOSE = Subgraph(
    name=SHARED_TEXTS["choose"],
    nodes=(
        Node("pad", HostNode.FORMAT, {"f_string": "{a} [-2, -2, -2, -2]"}),
        Node("first", HostNode.EXTRACT, {"regex_pattern": SCORES_PATTERN, "mode": "First Group", "group_index": 2}),
        Node("second", HostNode.EXTRACT, {"regex_pattern": SCORES_PATTERN, "mode": "First Group", "group_index": 3}),
        Node("third", HostNode.EXTRACT, {"regex_pattern": SCORES_PATTERN, "mode": "First Group", "group_index": 4}),
        Node("fourth", HostNode.EXTRACT, {"regex_pattern": SCORES_PATTERN, "mode": "First Group", "group_index": 5}),
        Node("first_score", HostNode.NUMBER),
        Node("second_score", HostNode.NUMBER),
        Node("third_score", HostNode.NUMBER),
        Node("fourth_score", HostNode.NUMBER),
        Node("best", HostNode.MATH, {"expression": "values.index(max(values))"}),
        Node("winner", HostNode.LIST_ITEM),
        Node("save", HostNode.SAVE_IMAGE, {"filename_prefix": "image/byteplus/hero"}),
    ),
    links=(
        ("pad.STRING", "first.string"),
        ("pad.STRING", "second.string"),
        ("pad.STRING", "third.string"),
        ("pad.STRING", "fourth.string"),
        ("first.STRING", "first_score.value"),
        ("second.STRING", "second_score.value"),
        ("third.STRING", "third_score.value"),
        ("fourth.STRING", "fourth_score.value"),
        ("first_score.FLOAT", "best.values.a"),
        ("second_score.FLOAT", "best.values.b"),
        ("third_score.FLOAT", "best.values.c"),
        ("fourth_score.FLOAT", "best.values.d"),
        ("best.INT", "winner.index"),
        ("winner.*", "save.images"),
    ),
    columns=(
        ("pad",),
        ("first", "second", "third", "fourth"),
        ("first_score", "second_score", "third_score", "fourth_score"),
        ("best", "winner"),
        ("save",),
    ),
    inputs=(("similarities", "pad.values.a"), ("images", "winner.list")),
    description=HERO_TEXTS["choose_description"],
    previews=(("save", IMAGE_PREVIEW),),
)

CHOOSE_HERO_IMAGE = Workflow(
    slug="search-01-choose-a-hero-image",
    nodes=(
        Node(
            "brief",
            HostNode.TEXT,
            {
                "value": (
                    "Trail running shoes in bright orange on a rocky mountain path at sunrise, wide shot, open sky on "
                    "the left for a headline."
                )
            },
            title=SHARED_TEXTS["brief"],
        ),
        Node("draw", DRAW.name),
        Node("score", EMBED.name),
        Node("scores", HostNode.PREVIEW, title=SHARED_TEXTS["scores"]),
        Node("choose", CHOOSE.name),
    ),
    links=(
        ("brief.STRING", "draw.brief"),
        ("brief.STRING", "score.brief"),
        ("draw.images", "score.images"),
        ("score.similarities", "scores.source"),
        ("score.similarities", "choose.similarities"),
        ("draw.images", "choose.images"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("brief",),), note=HERO_TEXTS["input"]),),
        (Group(SHARED_TEXTS["options"], (("draw",),), STAGE_COLOUR, HERO_TEXTS["draw"]),),
        (Group(SHARED_TEXTS["score"], (("score",), ("scores",)), STAGE_COLOUR, HERO_TEXTS["score"]),),
        (Group(SHARED_TEXTS["choose"], (("choose",),), STAGE_COLOUR, HERO_TEXTS["choose"]),),
    ),
    subgraphs=(DRAW, EMBED, CHOOSE),
)

SEARCH_WORKFLOWS = (CHOOSE_HERO_IMAGE,)

__all__ = ["SEARCH_WORKFLOWS"]
