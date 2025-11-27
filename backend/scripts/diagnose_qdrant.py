"""
Diagnostic script to check Qdrant connection and configuration
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from app.core.qdrant_manager import get_qdrant_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def diagnose_qdrant():
    """Diagnose Qdrant connection issues"""
    print("=" * 60)
    print("QDRANT CONNECTION DIAGNOSTIC")
    print("=" * 60)
    print()
    
    # Check environment variables
    print("1. Environment Variables:")
    print(f"   QDRANT_HOST: {os.getenv('QDRANT_HOST', 'localhost (default)')}")
    print(f"   QDRANT_PORT: {os.getenv('QDRANT_PORT', '6333 (default)')}")
    print(f"   QDRANT_URL: {os.getenv('QDRANT_URL', 'Not set')}")
    print(f"   QDRANT_API_KEY: {'Set' if os.getenv('QDRANT_API_KEY') else 'Not set'}")
    print(f"   QDRANT_COLLECTION_NAME: {os.getenv('QDRANT_COLLECTION_NAME', 'srmu_documents (default)')}")
    print()
    
    # Try to initialize Qdrant manager
    print("2. Initializing Qdrant Manager...")
    try:
        qdrant_manager = get_qdrant_manager()
        print(f"   ✅ QdrantManager initialized successfully")
        print(f"   URL: {qdrant_manager.qdrant_url}")
        print(f"   Collection: {qdrant_manager.collection_name}")
        print()
    except Exception as e:
        print(f"   ❌ Failed to initialize QdrantManager: {str(e)}")
        return
    
    # Test health check
    print("3. Testing Health Check...")
    is_healthy, error_msg = qdrant_manager.health_check()
    if is_healthy:
        print("   ✅ Qdrant service is healthy")
        print()
        
        # Get collection info
        print("4. Collection Information:")
        try:
            collection_info = qdrant_manager.get_collection_info()
            print(f"   Collection Name: {qdrant_manager.collection_name}")
            print(f"   Points Count: {collection_info.get('points_count', 'N/A')}")
            print(f"   Vectors Count: {collection_info.get('vectors_count', 'N/A')}")
            print(f"   Status: {collection_info.get('status', 'N/A')}")
        except Exception as e:
            print(f"   ⚠️  Could not get collection info: {str(e)}")
            print("   (Collection might not exist yet)")
    else:
        print(f"   ❌ Qdrant service is NOT available")
        print(f"   Error: {error_msg}")
        print()
        print("5. Troubleshooting:")
        print()
        
        if "Connection refused" in error_msg or "Failed to connect" in error_msg:
            print("   Issue: Cannot connect to Qdrant server")
            print("   Solutions:")
            print("   - If using local Qdrant, make sure it's running:")
            print("     docker run -p 6333:6333 qdrant/qdrant")
            print("   - Check if QDRANT_HOST and QDRANT_PORT are correct")
            print("   - Verify network connectivity")
        elif "Unauthorized" in error_msg or "401" in error_msg or "403" in error_msg:
            print("   Issue: Authentication failed")
            print("   Solutions:")
            print("   - Check if QDRANT_API_KEY is correct")
            print("   - Verify your Qdrant Cloud API key")
        elif "Not found" in error_msg or "404" in error_msg:
            print("   Issue: Qdrant endpoint not found")
            print("   Solutions:")
            print("   - Check if QDRANT_URL is correct")
            print("   - Verify the Qdrant service URL")
        else:
            print(f"   Unknown error: {error_msg}")
            print("   Solutions:")
            print("   - Check Qdrant service logs")
            print("   - Verify network connectivity")
            print("   - Check firewall settings")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    diagnose_qdrant()


