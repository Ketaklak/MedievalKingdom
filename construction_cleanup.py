#!/usr/bin/env python3
"""
Construction Queue Data Cleanup Script
Fix buildings that are marked as constructing but have no queue items
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Get backend URL from frontend .env file
def get_backend_url():
    """Get backend URL from frontend .env file"""
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
    return "http://localhost:8001"

BASE_URL = get_backend_url()
API_URL = f"{BASE_URL}/api"

async def cleanup_construction_data():
    """Cleanup construction data inconsistencies"""
    print("🔧 Construction Queue Data Cleanup")
    print(f"🔗 API at: {API_URL}")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Login as admin
        admin_login_data = {
            "username": "admin",
            "password": "admin"
        }
        
        async with session.post(f"{API_URL}/auth/login", json=admin_login_data) as response:
            login_data = await response.json()
            if response.status != 200:
                print(f"❌ Failed to login: {login_data}")
                return
            
            admin_token = login_data['access_token']
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            print("✅ Admin login successful")
            
            # Get current building states
            async with session.get(f"{API_URL}/game/player/buildings", headers=headers) as response:
                buildings_data = await response.json()
                if response.status != 200:
                    print(f"❌ Failed to get buildings: {buildings_data}")
                    return
                
                buildings = buildings_data.get('buildings', [])
                constructing_buildings = [b for b in buildings if b.get('constructing', False)]
                
                print(f"📊 Found {len(constructing_buildings)} buildings marked as constructing")
                
                # Get construction queue
                async with session.get(f"{API_URL}/game/construction/queue", headers=headers) as response:
                    queue_data = await response.json()
                    if response.status != 200:
                        print(f"❌ Failed to get construction queue: {queue_data}")
                        return
                    
                    queue = queue_data.get('queue', [])
                    print(f"📊 Found {len(queue)} items in construction queue")
                    
                    if len(constructing_buildings) > 0 and len(queue) == 0:
                        print("🔧 Data inconsistency detected: buildings marked as constructing but no queue items")
                        print("   This suggests constructions were completed but building states weren't updated")
                        print("   The background task fix should prevent this in the future")
                        print("   For now, these buildings will remain constructing until manually fixed")
                        
                        for building in constructing_buildings:
                            print(f"   - {building.get('type', 'unknown')} (Level {building.get('level', 1)}) - ID: {building.get('id', 'unknown')}")
                    
                    elif len(constructing_buildings) == len(queue):
                        print("✅ Construction data is consistent")
                    
                    else:
                        print(f"⚠️  Partial inconsistency: {len(constructing_buildings)} constructing buildings vs {len(queue)} queue items")

if __name__ == "__main__":
    asyncio.run(cleanup_construction_data())