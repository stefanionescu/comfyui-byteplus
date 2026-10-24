"""The names this extension uses in spaces shared with other packs."""

# Every node identifier is this prefix and the class name.
NODE_PREFIX = 'BytePlus'

# The menu headings that group the nodes. Code calls 3D nodes `mesh` because a name cannot start with a digit.
MENUS = {
    'SHARED': 'BytePlus',
    'CHAT': 'BytePlus/Chat',
    'IMAGE': 'BytePlus/Image',
    'VIDEO': 'BytePlus/Video',
    'SEARCH': 'BytePlus/Search',
    'MESH': 'BytePlus/3D',
}

# The socket types more than one node shares, prefixed so no other pack's socket of the same name connects.
SOCKET_TYPES = {
    'OPTIONS': 'BYTEPLUS_OPTIONS',
    'DOCUMENTS': 'BYTEPLUS_DOCUMENTS',
    'CONVERSATION': 'BYTEPLUS_CONVERSATION',
    'REFERENCES': 'BYTEPLUS_REFERENCES',
}

__all__ = [
    'MENUS',
    'NODE_PREFIX',
    'SOCKET_TYPES',
]
