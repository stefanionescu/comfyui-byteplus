"""3D choices, the commands each 3D model reads in its text item, the limits of a source image, and the 3D file."""

from .inputs import MODEL_DEFAULT

# The kind of a 3D task's record, which 3D: Download lists and collects.
JOB_KIND = "meshes"

# The texture, mesh, precision, and pose choices; model default sends no command.
TEXTURES = (MODEL_DEFAULT, "white", "textured", "PBR")
TOPOLOGIES = (MODEL_DEFAULT, "triangles", "quads")
PRECISIONS = (MODEL_DEFAULT, "standard", "high")
POSES = (MODEL_DEFAULT, "T or A pose")

# The sides an image can show, in Hitem3D's order, and the separator between them in the views input.
VIEWS = ("front", "back", "left", "right")
VIEW_SEPARATOR = ","

# The largest face count either model takes.
MAX_FACES = 2_000_000

# Each command set's spelling of a setting, as each model's page writes it; a command set missing from a table does
# not take that setting, and the model row refuses it first.
TEXTURE_COMMANDS = {
    "hyper3d": {"white": "--material None", "textured": "--material Shaded", "PBR": "--material PBR"},
    "hitem3d": {"white": "--request_type 1", "textured": "--request_type 3"},
}
TOPOLOGY_COMMANDS = {"hyper3d": {"triangles": "--mesh_mode Raw", "quads": "--mesh_mode Quad"}}
PRECISION_COMMANDS = {"hitem3d": {"standard": "--resolution 1536", "high": "--resolution 1536pro"}}
POSE_COMMANDS = {"hyper3d": {"T or A pose": "--TAPose true"}}
FACE_COMMANDS = {"hyper3d": "--quality_override {faces}", "hitem3d": "--face {faces}"}
# {bits} holds one character per side of VIEWS: 1 where an image shows that side.
VIEW_COMMANDS = {"hitem3d": "--multi_images_bit {bits}"}
# GLB is always asked for, since Hitem3D makes OBJ by default.
FORMAT_COMMANDS = {"hyper3d": "--fileformat glb", "hitem3d": "--ff 2"}

# Every command either model reads, short forms included; a prompt holding one is refused.
COMMAND_NAMES = (
    "material",
    "mesh_mode",
    "quality_override",
    "subdivisionlevel",
    "sl",
    "addons",
    "use_original_alpha",
    "bbox_condition",
    "TAPose",
    "fileformat",
    "ff",
    "hd_texture",
    "resolution",
    "face",
    "request_type",
    "multi_images_bit",
)

# Hyper3D takes source images of less than 4096 by 4096 pixels and less than 30 MB.
IMAGE_PIXELS_BELOW = 4096 * 4096
IMAGE_BYTES_BELOW = 30_000_000

# The 3D file's format, and the first four bytes of every GLB file.
FILE_FORMAT = "glb"
GLB_SIGNATURE = b"glTF"

# The time between a 3D task's status checks; the first check is immediate.
POLL_INTERVAL_SECONDS = 10

__all__ = [
    "COMMAND_NAMES",
    "FACE_COMMANDS",
    "FILE_FORMAT",
    "FORMAT_COMMANDS",
    "GLB_SIGNATURE",
    "IMAGE_BYTES_BELOW",
    "IMAGE_PIXELS_BELOW",
    "JOB_KIND",
    "MAX_FACES",
    "POLL_INTERVAL_SECONDS",
    "POSES",
    "POSE_COMMANDS",
    "PRECISIONS",
    "PRECISION_COMMANDS",
    "TEXTURES",
    "TEXTURE_COMMANDS",
    "TOPOLOGIES",
    "TOPOLOGY_COMMANDS",
    "VIEWS",
    "VIEW_COMMANDS",
    "VIEW_SEPARATOR",
]
