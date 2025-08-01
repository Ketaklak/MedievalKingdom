#!/usr/bin/env python3
"""
Construction Queue Debug Test
Specifically debug the construction queue issue reported by user
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

async def debug_construction_queue():
    """Debug construction queue system"""
    print("🔍 Construction Queue Debug Test")
    print(f"🔗 Testing API at: {API_URL}")
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
            
            # 1. Get player buildings to see current state
            print("\n1. Checking current building states...")
            async with session.get(f"{API_URL}/game/player/buildings", headers=headers) as response:
                buildings_data = await response.json()
                if response.status == 200:
                    buildings = buildings_data.get('buildings', [])
                    print(f"✅ Found {len(buildings)} buildings:")
                    for building in buildings:
                        constructing = building.get('constructing', False)
                        print(f"   - {building.get('type', 'unknown')} (Level {building.get('level', 1)}) - Constructing: {constructing}")
                else:
                    print(f"❌ Failed to get buildings: {buildings_data}")
                    return
            
            # 2. Get construction queue
            print("\n2. Checking construction queue...")
            async with session.get(f"{API_URL}/game/construction/queue", headers=headers) as response:
                queue_data = await response.json()
                if response.status == 200:
                    queue = queue_data.get('queue', [])
                    print(f"✅ Construction queue has {len(queue)} items:")
                    for item in queue:
                        print(f"   - Building: {item.get('buildingType', 'unknown')} -> Level {item.get('targetLevel', 'unknown')}")
                        print(f"     Start: {item.get('startTime', 'unknown')}")
                        print(f"     Completion: {item.get('completionTime', 'unknown')}")
                        print(f"     Completed: {item.get('completed', 'unknown')}")
                else:
                    print(f"❌ Failed to get construction queue: {queue_data}")
                    return
            
            # 3. Try to find a building that's not constructing to upgrade
            print("\n3. Attempting to upgrade a non-constructing building...")
            non_constructing_buildings = [b for b in buildings if not b.get('constructing', False)]
            
            if non_constructing_buildings:
                target_building = non_constructing_buildings[0]
                print(f"   Targeting: {target_building.get('type', 'unknown')} (ID: {target_building.get('id', 'unknown')})")
                
                upgrade_data = {"buildingId": target_building.get('id')}
                async with session.post(f"{API_URL}/game/buildings/upgrade", json=upgrade_data, headers=headers) as response:
                    upgrade_response = await response.json()
                    if response.status == 200:
                        print(f"✅ Building upgrade started successfully: {upgrade_response}")
                    else:
                        print(f"❌ Building upgrade failed: {upgrade_response}")
            else:
                print("   ⚠️  All buildings are currently constructing")
            
            # 4. Check construction queue again after upgrade attempt
            print("\n4. Checking construction queue after upgrade attempt...")
            async with session.get(f"{API_URL}/game/construction/queue", headers=headers) as response:
                queue_data = await response.json()
                if response.status == 200:
                    queue = queue_data.get('queue', [])
                    print(f"✅ Construction queue now has {len(queue)} items:")
                    for item in queue:
                        print(f"   - Building: {item.get('buildingType', 'unknown')} -> Level {item.get('targetLevel', 'unknown')}")
                        print(f"     Start: {item.get('startTime', 'unknown')}")
                        print(f"     Completion: {item.get('completionTime', 'unknown')}")
                        print(f"     Completed: {item.get('completed', 'unknown')}")
                else:
                    print(f"❌ Failed to get construction queue: {queue_data}")
            
            # 5. Check building states again
            print("\n5. Checking building states after upgrade attempt...")
            async with session.get(f"{API_URL}/game/player/buildings", headers=headers) as response:
                buildings_data = await response.json()
                if response.status == 200:
                    buildings = buildings_data.get('buildings', [])
                    print(f"✅ Building states after upgrade:")
                    for building in buildings:
                        constructing = building.get('constructing', False)
                        print(f"   - {building.get('type', 'unknown')} (Level {building.get('level', 1)}) - Constructing: {constructing}")
                else:
                    print(f"❌ Failed to get buildings: {buildings_data}")
            
            # 6. Get player profile to check userId
            print("\n6. Checking player profile for userId...")
            async with session.get(f"{API_URL}/game/player/profile", headers=headers) as response:
                profile_data = await response.json()
                if response.status == 200:
                    profile = profile_data.get('profile', {})
                    user_id = profile.get('userId') or profile.get('id') or profile.get('_id')
                    print(f"✅ Player profile userId: {user_id}")
                    print(f"   Username: {profile.get('username', 'unknown')}")
                    print(f"   Kingdom: {profile.get('kingdomName', 'unknown')}")
                else:
                    print(f"❌ Failed to get profile: {profile_data}")

if __name__ == "__main__":
    asyncio.run(debug_construction_queue())