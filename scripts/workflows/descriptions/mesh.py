"""The 3D workflow: draw a character in a T-pose, turn it into a 3D model, and recover a task left running."""

from __future__ import annotations

from scripts.nodes.host import HostNode
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.page.config import STAGE_COLOUR, IMAGE_PREVIEW
from scripts.workflows.descriptions.nodes import MESH_DOWNLOAD, MESH_GENERATE, IMAGE_GENERATE
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.descriptions.texts import SHARED_TEXTS

CHARACTER_TEXTS = WORKFLOW_TEXTS['3d-01-turn-a-character-into-a-3d-model']

DESIGN = Subgraph(
    name=SHARED_TEXTS['pose'],
    nodes=(
        Node(
            'prompt',
            HostNode.FORMAT,
            {
                'f_string': (
                    'Full-body game character, standing in a T-pose, front view, plain white background, soft even '
                    'light, no shadows. {a}'
                )
            },
        ),
        Node('draw', IMAGE_GENERATE, is_paid=True),
        Node('look', HostNode.PREVIEW_IMAGE),
    ),
    links=(('prompt.STRING', 'draw.prompt'), ('draw.images', 'look.images')),
    columns=(('prompt',), ('draw',), ('look',)),
    inputs=(('character', 'prompt.values.a'),),
    outputs=(('image', 'draw.images'),),
    description=CHARACTER_TEXTS['design_description'],
    previews=(('look', IMAGE_PREVIEW),),
)

CHARACTER_MODEL = Workflow(
    slug='3d-01-turn-a-character-into-a-3d-model',
    nodes=(
        Node(
            'character',
            HostNode.TEXT_BLOCK,
            {
                'value': (
                    'A friendly robot gardener with a round body, a watering can for one hand, and green moss on its '
                    'shoulders.'
                )
            },
            title=SHARED_TEXTS['character'],
        ),
        Node('design', DESIGN.name),
        Node('mesh', MESH_GENERATE, {'prompt': '--material PBR --TAPose true'}, is_paid=True),
        Node('save', HostNode.SAVE_MESH, {'filename_prefix': '3d/byteplus/character'}),
        Node('download', MESH_DOWNLOAD, {'task': ''}, is_bypassed=True),
        Node('recovered', HostNode.SAVE_MESH, {'filename_prefix': '3d/byteplus/recovered'}, is_bypassed=True),
    ),
    links=(
        ('character.STRING', 'design.character'),
        ('design.image', 'mesh.images'),
        ('mesh.model_3d', 'save.mesh'),
        ('download.model_3d', 'recovered.mesh'),
    ),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('character',),), note=CHARACTER_TEXTS['input']),),
        (Group(SHARED_TEXTS['pose'], (('design',),), STAGE_COLOUR, CHARACTER_TEXTS['design']),),
        (
            Group(SHARED_TEXTS['build'], (('mesh',), ('save',)), STAGE_COLOUR, CHARACTER_TEXTS['build']),
            Group(SHARED_TEXTS['recover'], (('download',), ('recovered',)), STAGE_COLOUR, CHARACTER_TEXTS['recover']),
        ),
    ),
    subgraphs=(DESIGN,),
)

MESH_WORKFLOWS = (CHARACTER_MODEL,)

__all__ = ['MESH_WORKFLOWS']
