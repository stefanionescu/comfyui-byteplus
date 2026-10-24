"""The multimodal embedding row: what it reads and the embedding controls it takes."""

EMBEDDING_ROWS = {
    'skylark-embedding-vision-251215': {
        'kinds': ('embeddings',),
        'inputs': ('text', 'image', 'video'),
        'embedding': {'context': 131_072, 'dimensions': (1024, 2048)},
        'sources': ('model-list', 'multimodal-vectorization-api', 'vectorization'),
    },
}

__all__ = ['EMBEDDING_ROWS']
