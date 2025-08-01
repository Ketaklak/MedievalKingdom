#!/usr/bin/env python3
"""
Test to check current_user structure
"""

import asyncio
import aiohttp
import json

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

async def test_current_user():
    """Test current user endpoint"""
    print("🔍 Testing Current User Structure")
    
    async with aiohttp.ClientSession() as session:
        # First login as admin
        admin_login_data = {
            "username": "admin",
            "password": "admin"
        }
        
        async with session.post(f"{API_URL}/auth/login", json=admin_login_data) as response:
            if response.status == 200:
                data = await response.json()
                admin_token = data.get('access_token')
                print(f"✅ Admin login successful")
                
                # Test get current user
                headers = {"Authorization": f"Bearer {admin_token}"}
                
                async with session.get(f"{API_URL}/auth/me", headers=headers) as me_response:
                    print(f"Current user response status: {me_response.status}")
                    if me_response.status == 200:
                        me_data = await me_response.json()
                        print(f"Current user data: {json.dumps(me_data, indent=2, default=str)}")
                    else:
                        me_text = await me_response.text()
                        print(f"Current user error: {me_text}")
            else:
                print(f"❌ Admin login failed: {response.status}")

if __name__ == "__main__":
    asyncio.run(test_current_user())