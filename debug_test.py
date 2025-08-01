#!/usr/bin/env python3
"""
Debug test to check specific database operations
"""

import asyncio
import aiohttp
import json
import os
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

async def test_chat_debug():
    """Debug chat message sending"""
    print("🔍 Debug: Testing Chat Message Sending")
    
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
                print(f"✅ Admin login successful, token: {admin_token[:20]}...")
                
                # Test sending a chat message
                message_data = {
                    "content": "Debug test message from backend testing"
                }
                
                headers = {"Authorization": f"Bearer {admin_token}"}
                
                async with session.post(f"{API_URL}/chat/global", json=message_data, headers=headers) as chat_response:
                    print(f"Chat response status: {chat_response.status}")
                    try:
                        chat_data = await chat_response.json()
                        print(f"Chat response data: {chat_data}")
                    except:
                        chat_text = await chat_response.text()
                        print(f"Chat response text: {chat_text}")
            else:
                print(f"❌ Admin login failed: {response.status}")
                text = await response.text()
                print(f"Response: {text}")

async def test_trade_debug():
    """Debug trade offer creation"""
    print("🔍 Debug: Testing Trade Offer Creation")
    
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
                
                # Test creating a trade offer
                trade_data = {
                    "offering": {"gold": 100, "wood": 50},
                    "requesting": {"stone": 75, "food": 25},
                    "duration": 3600
                }
                
                headers = {"Authorization": f"Bearer {admin_token}"}
                
                async with session.post(f"{API_URL}/diplomacy/trade/create", json=trade_data, headers=headers) as trade_response:
                    print(f"Trade response status: {trade_response.status}")
                    try:
                        trade_data = await trade_response.json()
                        print(f"Trade response data: {trade_data}")
                    except:
                        trade_text = await trade_response.text()
                        print(f"Trade response text: {trade_text}")
            else:
                print(f"❌ Admin login failed: {response.status}")

async def main():
    """Main debug function"""
    print("🔍 Medieval Empires Backend Debug Tests")
    print(f"🔗 Testing API at: {API_URL}")
    print("=" * 60)
    
    await test_chat_debug()
    print()
    await test_trade_debug()

if __name__ == "__main__":
    asyncio.run(main())