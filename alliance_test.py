#!/usr/bin/env python3
"""
Test alliance creation after leaving current alliance
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

async def test_alliance_creation():
    """Test alliance creation after leaving current alliance"""
    
    async with aiohttp.ClientSession() as session:
        # Login as admin
        admin_login_data = {
            "username": "admin",
            "password": "admin"
        }
        
        async with session.post(f"{API_URL}/auth/login", json=admin_login_data) as response:
            login_data = await response.json()
            admin_token = login_data['access_token']
            print(f"✅ Admin login successful")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Check current alliance
        async with session.get(f"{API_URL}/diplomacy/alliance/my", headers=headers) as response:
            my_alliance_data = await response.json()
            current_alliance = my_alliance_data.get('alliance')
            
            if current_alliance:
                print(f"📋 Admin is currently in alliance: {current_alliance['name']}")
                
                # Leave current alliance
                async with session.post(f"{API_URL}/diplomacy/alliance/leave", headers=headers) as leave_response:
                    leave_data = await leave_response.json()
                    if leave_response.status == 200:
                        print(f"✅ Successfully left alliance: {leave_data}")
                    else:
                        print(f"❌ Failed to leave alliance: {leave_data}")
            else:
                print(f"📋 Admin is not in any alliance")
        
        # Now test creating a new alliance
        import uuid
        unique_name = f"New Test Alliance {str(uuid.uuid4())[:8]}"
        alliance_data = {
            "name": unique_name,
            "description": "A newly created alliance for testing purposes!"
        }
        
        async with session.post(f"{API_URL}/diplomacy/alliance/create", json=alliance_data, headers=headers) as response:
            create_data = await response.json()
            
            if response.status == 200:
                print(f"✅ Alliance creation successful: {create_data}")
                
                # Check serialization
                alliance = create_data.get('alliance', {})
                serialization_ok = True
                
                # Check ID is string
                if 'id' in alliance and not isinstance(alliance['id'], str):
                    serialization_ok = False
                    print(f"❌ ID serialization issue: {type(alliance['id'])}")
                
                # Check dates are ISO format strings
                if 'createdAt' in alliance:
                    date_val = alliance['createdAt']
                    if not isinstance(date_val, str):
                        serialization_ok = False
                        print(f"❌ Date serialization issue: {type(date_val)}")
                    else:
                        try:
                            datetime.fromisoformat(date_val.replace('Z', '+00:00'))
                            print(f"✅ Date serialization OK: {date_val}")
                        except:
                            serialization_ok = False
                            print(f"❌ Date format issue: {date_val}")
                
                if serialization_ok:
                    print(f"✅ All serialization checks passed")
                else:
                    print(f"❌ Serialization issues detected")
                    
            else:
                print(f"❌ Alliance creation failed: Status {response.status}, Response: {create_data}")

if __name__ == "__main__":
    asyncio.run(test_alliance_creation())