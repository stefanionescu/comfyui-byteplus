"""Function policy location, closed schema members and the host methods it exempts."""

FUNCTION_POLICY_PATH = "quality/config/repository/functions.json"
FUNCTION_POLICY_VERSION = 1
# ComfyUI calls these methods on a node class itself, so they cannot be inlined at a caller.
# The paid nodes and the Download nodes reach ComfyNode through the extension's shared base classes.
HOST_NODE_BASES = ("comfy_api.latest.io.ComfyNode", "src.nodes.base.PaidNode", "src.nodes.base.TaskDownload")
HOST_NODE_HOOKS = ("define_schema", "execute", "fingerprint_inputs", "validate_inputs")
