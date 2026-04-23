import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv('../.env')

c = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API_KEY'),
    check_compatibility=False
)

# Check collection info
info = c.get_collection('srmu_documents')
print(f"Points count: {info.points_count}")

# Get sample points
results = c.scroll(collection_name='srmu_documents', limit=3)
for p in results[0]:
    text = p.payload.get('text', 'NO TEXT KEY')
    print(f"\nID: {p.id}")
    print(f"  Payload keys: {list(p.payload.keys())}")
    print(f"  Text preview: {text[:150]}...")
