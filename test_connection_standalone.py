#!/usr/bin/env python3
"""
Standalone connection test for OpenProject MCP Server
"""
import asyncio
import os
import sys
import json
import base64
from datetime import datetime
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENPROJECT_URL = os.getenv("OPENPROJECT_URL", "http://localhost:3000")
OPENPROJECT_API_KEY = os.getenv("OPENPROJECT_API_KEY", "")

async def test_openproject_connection():
    """Test connection to OpenProject API."""
    print("🔗 Testing OpenProject connection...")
    print(f"URL: {OPENPROJECT_URL}")
    print(f"API Key: {'CONFIGURED' if OPENPROJECT_API_KEY else 'NOT_SET'}")
    
    if not OPENPROJECT_API_KEY or OPENPROJECT_API_KEY == "your_40_character_api_key_here":
        print("❌ API Key not configured in .env file")
        return False
    
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'apikey:{OPENPROJECT_API_KEY}'.encode()).decode()}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test with root API endpoint
            async with session.get(f"{OPENPROJECT_URL}/api/v3", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    version = data.get("coreVersion", "unknown")
                    print(f"✅ Connection successful! OpenProject version: {version}")
                    return True
                elif response.status == 401:
                    print("❌ Authentication failed - check your API key")
                    return False
                else:
                    text = await response.text()
                    print(f"❌ Connection failed - HTTP {response.status}: {text}")
                    return False
                    
    except aiohttp.ClientConnectorError:
        print(f"❌ Cannot connect to {OPENPROJECT_URL} - check URL and network")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

async def test_create_project():
    """Test project creation."""
    if not await test_openproject_connection():
        return None
    
    print("\n📁 Testing project creation...")
    
    # Generate unique project name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_name = f"Test Project {timestamp}"
    
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'apikey:{OPENPROJECT_API_KEY}'.encode()).decode()}",
        "Content-Type": "application/json"
    }
    
    project_data = {
        "name": project_name,
        "description": {
            "raw": "Test project created via MCP API"
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{OPENPROJECT_URL}/api/v3/projects",
                headers=headers,
                json=project_data
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    project_id = data.get("id")
                    print(f"✅ Project created successfully!")
                    print(f"   - ID: {project_id}")
                    print(f"   - Name: {data.get('name')}")
                    print(f"   - URL: {OPENPROJECT_URL}/projects/{data.get('identifier', project_id)}")
                    return project_id
                else:
                    text = await response.text()
                    print(f"❌ Project creation failed - HTTP {response.status}: {text}")
                    return None
                    
    except Exception as e:
        print(f"❌ Project creation error: {str(e)}")
        return None

async def main():
    """Main test function."""
    print("🧪 OpenProject MCP Connection Test")
    print("=" * 50)
    
    # Test basic connection
    if await test_openproject_connection():
        print("\n✅ Basic connection test passed!")
        
        # Test project creation
        project_id = await test_create_project()
        if project_id:
            print(f"\n🎉 Full API test successful!")
            print(f"🌐 View project: {OPENPROJECT_URL}/projects/{project_id}")
            return True
        else:
            print("\n⚠️  Connection works but project creation failed")
            return False
    else:
        print("\n❌ Connection test failed")
        print("\nNext steps:")
        print("1. Check your OpenProject URL in .env")
        print("2. Verify your API key in .env")
        print("3. Ensure OpenProject is running and accessible")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        sys.exit(1)
