"""3D task constants: the file format command each 3D model reads, the limits of a source image, and the 3D file."""

# The kind of a 3D task's record, which 3D: Download lists and collects.
JOB_KIND = "meshes"

# GLB is always asked for, since Hitem3D makes OBJ by default: each command set's command, as each model's page writes
# it, and the value that names GLB in it.
FORMAT_COMMANDS = {"hyper3d": "--fileformat glb", "hitem3d": "--ff 2"}
GLB_FORMATS = {"hyper3d": "glb", "hitem3d": "2"}

# Hyper3D takes source images of less than 4096 by 4096 pixels and less than 30 MB.
IMAGE_PIXELS_BELOW = 4096 * 4096
IMAGE_BYTES_BELOW = 30_000_000

# The 3D file's format, and the first four bytes of every GLB file.
FILE_FORMAT = "glb"
GLB_SIGNATURE = b"glTF"

# The time between a 3D task's status checks; the first check is immediate.
POLL_INTERVAL_SECONDS = 10

__all__ = [
    "FILE_FORMAT",
    "FORMAT_COMMANDS",
    "GLB_FORMATS",
    "GLB_SIGNATURE",
    "IMAGE_BYTES_BELOW",
    "IMAGE_PIXELS_BELOW",
    "JOB_KIND",
    "POLL_INTERVAL_SECONDS",
]
