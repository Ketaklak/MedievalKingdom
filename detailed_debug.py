#!/usr/bin/env python3
"""
Test to debug the specific 500 error
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

async def test_detailed_debug():
    """Debug with detailed error checking"""
    print("🔍 Detailed Debug Test")
    
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
                
                # Check player data structure
                headers = {"Authorization": f"Bearer {admin_token}"}
                
                async with session.get(f"{API_URL}/auth/me", headers=headers) as me_response:
                    if me_response.status == 200:
                        me_data = await me_response.json()
                        player = me_data.get('player', {})
                        print(f"Player username: {player.get('username', 'MISSING')}")
                        print(f"Player empire: {player.get('empire', 'MISSING')}")
                        print(f"Player userId: {player.get('userId', 'MISSING')}")
                        
                        # Test a simple message
                        message_data = {
                            "content": "Simple test message"
                        }
                        
                        async with session.post(f"{API_URL}/chat/global", json=message_data, headers=headers) as chat_response:
                            print(f"Chat response status: {chat_response.status}")
                            print(f"Chat response headers: {dict(chat_response.headers)}")
                            
                            if chat_response.status != 200:
                                try:
                                    error_data = await chat_response.json()
                                    print(f"Chat error JSON: {error_data}")
                                except:
                                    error_text = await chat_response.text()
                                    print(f"Chat error text: {error_text}")
                            else:
                                success_data = await chat_response.json()
                                print(f"Chat success: {success_data}")
                    else:
                        print(f"❌ Failed to get current user: {me_response.status}")
            else:
                print(f"❌ Admin login failed: {response.status}")

if __name__ == "__main__":
    asyncio.run(test_detailed_debug())