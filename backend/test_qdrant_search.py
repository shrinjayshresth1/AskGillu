import os
import numpy as np
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv('../.env')

c = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API_KEY'),
    check_compatibility=False
)

# Get a sample vector to use as a query (search with an existing point's vector)
results = c.scroll(collection_name='srmu_documents', limit=1, with_vectors=True)
sample_vector = results[0][0].vector

# Search with this vector
search_results = c.search(
    collection_name='srmu_documents',
    query_vector=sample_vector,
    limit=3,
    score_threshold=0.0
)

print(f"Search results: {len(search_results)}")
for r in search_results:
    print(f"\n  Score: {r.score:.4f}")
    print(f"  Text: {r.payload.get('text', '')[:200]}...")

# Check vector dimension
print(f"\nVector dimension: {len(sample_vector)}")

# Check collection config
info = c.get_collection('srmu_documents')
print(f"Collection distance: {info.config.params.vectors.distance}")
print(f"Collection vector size: {info.config.params.vectors.size}")
