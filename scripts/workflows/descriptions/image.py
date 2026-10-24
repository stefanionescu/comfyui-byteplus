"""The image workflows: design a character and pose it again, make a poster series, and split a poster into layers."""

from __future__ import annotations

from scripts.nodes.host import HostNode
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.page.config import STAGE_COLOUR, IMAGE_PREVIEW
from scripts.workflows.descriptions.nodes import MODEL_REPORT, IMAGE_GENERATE, SEEDREAM_MODEL, IMAGE_SPLIT_LAYERS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.descriptions.texts import SHARED_TEXTS

POSTER_PROMPT = (
    'A poster for a summer night market: the title "Night Market" in bold hand-lettered type at the top, paper '
    'lanterns and food stalls in silhouette, and the date "August 14" at the bottom. Flat illustration in deep blue '
    'and orange.'
)
CHARACTER_TEXTS = WORKFLOW_TEXTS['image-01-design-a-character']
SERIES_TEXTS = WORKFLOW_TEXTS['image-02-make-a-poster-series']
LAYERS_TEXTS = WORKFLOW_TEXTS['image-03-split-a-poster-into-layers']

DESIGN = Subgraph(
    name=SHARED_TEXTS['design'],
    nodes=(
        Node(
            'prompt',
            HostNode.FORMAT,
            {'f_string': 'Character sheet: {a} Full body, front view, standing, plain light gray background.'},
        ),
        Node('draw', IMAGE_GENERATE, {'size': '1344x1792'}, is_paid=True),
        Node('save', HostNode.SAVE_IMAGE, {'filename_prefix': 'image/byteplus/character'}),
    ),
    links=(('prompt.STRING', 'draw.prompt'), ('draw.images', 'save.images')),
    columns=(('prompt',), ('draw',), ('save',)),
    inputs=(('character', 'prompt.values.a'),),
    outputs=(('references', 'draw.references'),),
    description=CHARACTER_TEXTS['design_description'],
    previews=(('save', IMAGE_PREVIEW),),
)

WAVE = Subgraph(
    name=SHARED_TEXTS['wave'],
    nodes=(
        Node(
            'edit',
            IMAGE_GENERATE,
            {'size': '1344x1792', 'prompt': 'The character in Image 1, waving, same outfit'},
            is_paid=True,
        ),
        Node('save', HostNode.SAVE_IMAGE, {'filename_prefix': 'image/byteplus/character-waving'}),
    ),
    links=(('edit.images', 'save.images'),),
    columns=(('edit',), ('save',)),
    inputs=(('references', 'edit.references'),),
    description=CHARACTER_TEXTS['wave_description'],
    previews=(('save', IMAGE_PREVIEW),),
)

DESIGN_CHARACTER = Workflow(
    slug='image-01-design-a-character',
    nodes=(
        Node(
            'character',
            HostNode.TEXT_BLOCK,
            {
                'value': (
                    'An original character: a young courier in a green hooded cloak, with a brown leather satchel and '
                    'a brass compass on a chain.'
                )
            },
            title=SHARED_TEXTS['character'],
        ),
        Node('design', DESIGN.name),
        Node('wave', WAVE.name),
    ),
    links=(('character.STRING', 'design.character'), ('design.references', 'wave.references')),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('character',),), note=CHARACTER_TEXTS['input']),),
        (Group(SHARED_TEXTS['design'], (('design',),), STAGE_COLOUR, CHARACTER_TEXTS['design']),),
        (Group(SHARED_TEXTS['wave'], (('wave',),), STAGE_COLOUR, CHARACTER_TEXTS['wave']),),
    ),
    subgraphs=(DESIGN, WAVE),
)

SERIES = Subgraph(
    name=SHARED_TEXTS['series'],
    nodes=(
        Node(
            'draw',
            IMAGE_GENERATE,
            {'model': SEEDREAM_MODEL, 'size': '2848x1600', 'max_images': 4},
            is_paid=True,
        ),
        Node('save', HostNode.SAVE_IMAGE, {'filename_prefix': 'image/byteplus/poster-series'}),
    ),
    links=(('draw.images', 'save.images'),),
    columns=(('draw',), ('save',)),
    inputs=(('brief', 'draw.prompt'), ('model', 'draw.model')),
    description=SERIES_TEXTS['series_description'],
    previews=(('save', IMAGE_PREVIEW),),
)

POSTER_SERIES = Workflow(
    slug='image-02-make-a-poster-series',
    nodes=(
        Node(
            'brief',
            HostNode.TEXT_BLOCK,
            {
                'value': (
                    'Generate 4 travel posters for the same seaside town, one for each season, in one flat '
                    'illustration style, each with the town\'s name, "Port Ellis", at the top in the same typeface.'
                )
            },
            title=SHARED_TEXTS['brief'],
        ),
        Node('model', HostNode.TEXT, {'value': SEEDREAM_MODEL}, title=SHARED_TEXTS['model']),
        Node('info', MODEL_REPORT),
        Node('row', HostNode.PREVIEW, title=SHARED_TEXTS['info']),
        Node('series', SERIES.name),
    ),
    links=(
        ('brief.STRING', 'series.brief'),
        ('model.STRING', 'series.model'),
        ('model.STRING', 'info.model'),
        ('info.info', 'row.source'),
    ),
    stacks=(
        (
            Group(SHARED_TEXTS['input'], (('brief',),), note=SERIES_TEXTS['input']),
            Group(SHARED_TEXTS['model'], (('model', 'info'), ('row',)), note=SERIES_TEXTS['model']),
        ),
        (Group(SHARED_TEXTS['series'], (('series',),), STAGE_COLOUR, SERIES_TEXTS['series']),),
    ),
    subgraphs=(SERIES,),
)

DRAW = Subgraph(
    name=SHARED_TEXTS['draw'],
    nodes=(
        Node(
            'draw',
            IMAGE_GENERATE,
            {'size': '1344x1792', 'output_format': 'png'},
            is_paid=True,
        ),
        Node('save', HostNode.SAVE_IMAGE, {'filename_prefix': 'image/byteplus/poster'}),
    ),
    links=(('draw.images', 'save.images'),),
    columns=(('draw',), ('save',)),
    inputs=(('poster', 'draw.prompt'),),
    outputs=(('references', 'draw.references'),),
    description=LAYERS_TEXTS['draw_description'],
    previews=(('save', IMAGE_PREVIEW),),
)

SPLIT = Subgraph(
    name=SHARED_TEXTS['split'],
    nodes=(
        Node('split', IMAGE_SPLIT_LAYERS, is_paid=True),
        Node('join', HostNode.JOIN_ALPHA),
        Node('save_layers', HostNode.SAVE_IMAGE, {'filename_prefix': 'image/byteplus/poster-layers'}),
    ),
    links=(('split.layers', 'join.image'), ('split.masks', 'join.alpha'), ('join.IMAGE', 'save_layers.images')),
    columns=(('split',), ('join',), ('save_layers',)),
    inputs=(('poster', 'split.image'),),
    description=LAYERS_TEXTS['split_description'],
    previews=(('save_layers', IMAGE_PREVIEW),),
)

SPLIT_POSTER = Workflow(
    slug='image-03-split-a-poster-into-layers',
    nodes=(
        Node('poster', HostNode.TEXT_BLOCK, {'value': POSTER_PROMPT}, title=SHARED_TEXTS['poster']),
        Node('draw', DRAW.name),
        Node('split', SPLIT.name),
    ),
    links=(('poster.STRING', 'draw.poster'), ('draw.references', 'split.poster')),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('poster',),), note=LAYERS_TEXTS['input']),),
        (Group(SHARED_TEXTS['draw'], (('draw',),), STAGE_COLOUR, LAYERS_TEXTS['draw']),),
        (Group(SHARED_TEXTS['split'], (('split',),), STAGE_COLOUR, LAYERS_TEXTS['split']),),
    ),
    subgraphs=(DRAW, SPLIT),
)

IMAGE_WORKFLOWS = (DESIGN_CHARACTER, POSTER_SERIES, SPLIT_POSTER)

__all__ = ['IMAGE_WORKFLOWS']
