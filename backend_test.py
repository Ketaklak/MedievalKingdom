#!/usr/bin/env python3
"""
Medieval Empires Backend API Test Suite
Tests all backend endpoints and functionality
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

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

class MedievalEmpiresAPITester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.admin_token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
        if response_data and not success:
            print(f"    Response: {response_data}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, 
                          headers: Dict = None, use_auth: bool = False) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        try:
            url = f"{API_URL}{endpoint}"
            request_headers = headers or {}
            
            if use_auth and self.auth_token:
                request_headers["Authorization"] = f"Bearer {self.auth_token}"
            
            async with self.session.request(
                method, url, json=data, headers=request_headers
            ) as response:
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                return response.status < 400, response_data, response.status
                
        except Exception as e:
            return False, str(e), 0
    
    async def test_health_endpoints(self):
        """Test health check and status endpoints"""
        print("\n=== Testing Health & Status Endpoints ===")
        
        # Test health check
        success, data, status = await self.make_request("GET", "/")
        self.log_test(
            "Health Check (GET /api/)",
            success and status == 200,
            f"Status: {status}, Response: {data}"
        )
        
        # Test server status
        success, data, status = await self.make_request("GET", "/status")
        self.log_test(
            "Server Status (GET /api/status)",
            success and status == 200,
            f"Status: {status}, Database: {data.get('database', 'unknown') if isinstance(data, dict) else 'error'}"
        )
    
    async def test_authentication_system(self):
        """Test authentication endpoints"""
        print("\n=== Testing Authentication System ===")
        
        # Test user registration
        test_user_data = {
            "username": "testwarrior",
            "password": "strongpassword123",
            "email": "testwarrior@medievalempires.com",
            "kingdomName": "Test Kingdom",
            "empire": "norman"
        }
        
        success, data, status = await self.make_request("POST", "/auth/register", test_user_data)
        self.log_test(
            "User Registration (POST /api/auth/register)",
            success and status == 200,
            f"Status: {status}, User created: {data.get('user', {}).get('username', 'unknown') if isinstance(data, dict) else 'error'}"
        )
        
        if success and isinstance(data, dict) and 'access_token' in data:
            self.auth_token = data['access_token']
        
        # Test admin login
        admin_login_data = {
            "username": "admin",
            "password": "admin"
        }
        
        success, data, status = await self.make_request("POST", "/auth/login", admin_login_data)
        self.log_test(
            "Admin Login (POST /api/auth/login)",
            success and status == 200,
            f"Status: {status}, Admin logged in: {data.get('user', {}).get('isAdmin', False) if isinstance(data, dict) else 'error'}"
        )
        
        if success and isinstance(data, dict) and 'access_token' in data:
            self.admin_token = data['access_token']
        
        # Test get current user info
        success, data, status = await self.make_request("GET", "/auth/me", use_auth=True)
        self.log_test(
            "Get Current User (GET /api/auth/me)",
            success and status == 200,
            f"Status: {status}, Username: {data.get('user', {}).get('username', 'unknown') if isinstance(data, dict) else 'error'}"
        )
    
    async def test_game_features(self):
        """Test game feature endpoints"""
        print("\n=== Testing Game Features ===")
        
        if not self.auth_token:
            print("⚠️  Skipping game features - no auth token")
            return
        
        # Test get player resources
        success, data, status = await self.make_request("GET", "/game/player/resources", use_auth=True)
        self.log_test(
            "Get Player Resources (GET /api/game/player/resources)",
            success and status == 200,
            f"Status: {status}, Gold: {data.get('resources', {}).get('gold', 'unknown') if isinstance(data, dict) else 'error'}"
        )
        
        # Test get player buildings
        success, data, status = await self.make_request("GET", "/game/player/buildings", use_auth=True)
        self.log_test(
            "Get Player Buildings (GET /api/game/player/buildings)",
            success and status == 200,
            f"Status: {status}, Buildings count: {len(data.get('buildings', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # Test get player army
        success, data, status = await self.make_request("GET", "/game/player/army", use_auth=True)
        self.log_test(
            "Get Player Army (GET /api/game/player/army)",
            success and status == 200,
            f"Status: {status}, Soldiers: {data.get('army', {}).get('soldiers', 'unknown') if isinstance(data, dict) else 'error'}"
        )
        
        # Test get leaderboard
        success, data, status = await self.make_request("GET", "/game/leaderboard")
        self.log_test(
            "Get Leaderboard (GET /api/game/leaderboard)",
            success and status == 200,
            f"Status: {status}, Players count: {len(data.get('leaderboard', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # Test get nearby players
        success, data, status = await self.make_request("GET", "/game/players/nearby", use_auth=True)
        self.log_test(
            "Get Nearby Players (GET /api/game/players/nearby)",
            success and status == 200,
            f"Status: {status}, Nearby players: {len(data.get('players', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # Test get player profile
        success, data, status = await self.make_request("GET", "/game/player/profile", use_auth=True)
        self.log_test(
            "Get Player Profile (GET /api/game/player/profile)",
            success and status == 200,
            f"Status: {status}, Kingdom: {data.get('profile', {}).get('kingdomName', 'unknown') if isinstance(data, dict) else 'error'}"
        )
        
        # Test construction queue
        success, data, status = await self.make_request("GET", "/game/construction/queue", use_auth=True)
        self.log_test(
            "Get Construction Queue (GET /api/game/construction/queue)",
            success and status == 200,
            f"Status: {status}, Queue items: {len(data.get('queue', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # Test combat history
        success, data, status = await self.make_request("GET", "/game/combat/history", use_auth=True)
        self.log_test(
            "Get Combat History (GET /api/game/combat/history)",
            success and status == 200,
            f"Status: {status}, History items: {len(data.get('history', [])) if isinstance(data, dict) else 'error'}"
        )
    
    async def test_chat_system(self):
        """Test chat system endpoints"""
        print("\n=== Testing Chat System ===")
        
        # Test get global messages
        success, data, status = await self.make_request("GET", "/chat/global")
        self.log_test(
            "Get Global Messages (GET /api/chat/global)",
            success and status == 200,
            f"Status: {status}, Messages count: {len(data.get('messages', [])) if isinstance(data, dict) else 'error'}"
        )
        
        if not self.auth_token:
            print("⚠️  Skipping authenticated chat features - no auth token")
            return
        
        # Test send global message
        message_data = {
            "content": "Greetings from the test realm! The kingdom prospers under our rule."
        }
        
        success, data, status = await self.make_request("POST", "/chat/global", message_data, use_auth=True)
        self.log_test(
            "Send Global Message (POST /api/chat/global)",
            success and status == 200,
            f"Status: {status}, Message sent: {data.get('success', False) if isinstance(data, dict) else 'error'}"
        )
        
        # Test get online users
        success, data, status = await self.make_request("GET", "/chat/online-users")
        self.log_test(
            "Get Online Users (GET /api/chat/online-users)",
            success and status == 200,
            f"Status: {status}, Online users: {len(data.get('users', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # Test get private messages
        success, data, status = await self.make_request("GET", "/chat/private", use_auth=True)
        self.log_test(
            "Get Private Messages (GET /api/chat/private)",
            success and status == 200,
            f"Status: {status}, Private messages: {len(data.get('messages', [])) if isinstance(data, dict) else 'error'}"
        )
    
    async def test_admin_functions(self):
        """Test admin endpoints"""
        print("\n=== Testing Admin Functions ===")
        
        if not self.admin_token:
            print("⚠️  Skipping admin functions - no admin token")
            return
        
        # Temporarily use admin token for admin tests
        original_token = self.auth_token
        self.auth_token = self.admin_token
        
        # Test get admin stats
        success, data, status = await self.make_request("GET", "/admin/stats", use_auth=True)
        self.log_test(
            "Get Admin Stats (GET /api/admin/stats)",
            success and status == 200,
            f"Status: {status}, Total players: {data.get('stats', {}).get('totalPlayers', 'unknown') if isinstance(data, dict) else 'error'}"
        )
        
        # Test get all players
        success, data, status = await self.make_request("GET", "/admin/players", use_auth=True)
        self.log_test(
            "Get All Players (GET /api/admin/players)",
            success and status == 200,
            f"Status: {status}, Players count: {len(data.get('players', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # Test get system info
        success, data, status = await self.make_request("GET", "/admin/system-info", use_auth=True)
        self.log_test(
            "Get System Info (GET /api/admin/system-info)",
            success and status == 200,
            f"Status: {status}, CPU usage: {data.get('system', {}).get('cpu_usage', 'unknown') if isinstance(data, dict) else 'error'}"
        )
        
        # Test get all chat messages (admin)
        success, data, status = await self.make_request("GET", "/admin/chat-messages", use_auth=True)
        self.log_test(
            "Get All Chat Messages (GET /api/admin/chat-messages)",
            success and status == 200,
            f"Status: {status}, Messages count: {len(data.get('messages', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # Restore original token
        self.auth_token = original_token
    
    async def test_empire_bonuses(self):
        """Test empire bonuses functionality"""
        print("\n=== Testing Empire Bonuses ===")
        
        if not self.auth_token:
            print("⚠️  Skipping empire bonuses test - no auth token")
            return
        
        # Test getting resources which should include empire bonuses
        success, data, status = await self.make_request("GET", "/game/player/resources", use_auth=True)
        
        if success and isinstance(data, dict):
            empire_bonuses = data.get('empire_bonuses', {})
            has_bonuses = bool(empire_bonuses)
            
            self.log_test(
                "Empire Bonuses Applied",
                has_bonuses,
                f"Empire bonuses present: {has_bonuses}, Bonuses: {empire_bonuses}"
            )
        else:
            self.log_test(
                "Empire Bonuses Applied",
                False,
                f"Failed to get empire bonuses data: {data}"
            )
    
    async def test_resource_generation(self):
        """Test resource generation system"""
        print("\n=== Testing Resource Generation ===")
        
        if not self.auth_token:
            print("⚠️  Skipping resource generation test - no auth token")
            return
        
        # Test getting buildings which should include resource generation
        success, data, status = await self.make_request("GET", "/game/player/buildings", use_auth=True)
        
        if success and isinstance(data, dict):
            resource_generation = data.get('resource_generation', {})
            has_generation = bool(resource_generation)
            
            self.log_test(
                "Resource Generation System",
                has_generation,
                f"Resource generation active: {has_generation}, Generation: {resource_generation}"
            )
        else:
            self.log_test(
                "Resource Generation System",
                False,
                f"Failed to get resource generation data: {data}"
            )
    
    async def test_army_recruitment(self):
        """Test army recruitment functionality"""
        print("\n=== Testing Army Recruitment ===")
        
        if not self.auth_token:
            print("⚠️  Skipping army recruitment test - no auth token")
            return
        
        # Test recruiting soldiers
        recruit_data = {
            "unitType": "soldiers",
            "quantity": 5
        }
        
        success, data, status = await self.make_request("POST", "/game/army/recruit", recruit_data, use_auth=True)
        self.log_test(
            "Army Recruitment (POST /api/game/army/recruit)",
            success and status == 200,
            f"Status: {status}, Recruitment success: {data.get('success', False) if isinstance(data, dict) else 'error'}"
        )
    
    async def test_construction_queue_system(self):
        """Test construction queue system specifically"""
        print("\n=== Testing Construction Queue System (User Reported Issue) ===")
        
        if not self.admin_token:
            print("⚠️  Skipping construction queue test - no admin token")
            return
        
        # Use admin token for testing
        original_token = self.auth_token
        self.auth_token = self.admin_token
        
        # Test get construction queue
        success, data, status = await self.make_request("GET", "/game/construction/queue", use_auth=True)
        self.log_test(
            "Get Construction Queue (GET /api/game/construction/queue)",
            success and status == 200,
            f"Status: {status}, Queue items: {len(data.get('queue', [])) if isinstance(data, dict) else 'error'}, Response: {data}"
        )
        
        # Test building upgrade to add to construction queue
        if success and isinstance(data, dict):
            # Get player buildings first
            buildings_success, buildings_data, buildings_status = await self.make_request("GET", "/game/player/buildings", use_auth=True)
            
            if buildings_success and isinstance(buildings_data, dict):
                buildings = buildings_data.get('buildings', [])
                if buildings:
                    # Try to upgrade first building
                    first_building = buildings[0]
                    upgrade_data = {"buildingId": first_building.get("id")}
                    
                    upgrade_success, upgrade_response, upgrade_status = await self.make_request(
                        "POST", "/game/buildings/upgrade", upgrade_data, use_auth=True
                    )
                    
                    self.log_test(
                        "Start Building Upgrade (POST /api/game/buildings/upgrade)",
                        upgrade_success and upgrade_status == 200,
                        f"Status: {upgrade_status}, Success: {upgrade_response.get('success', False) if isinstance(upgrade_response, dict) else 'error'}, Response: {upgrade_response}"
                    )
        
        # Restore original token
        self.auth_token = original_token
    
    async def test_chat_message_sending(self):
        """Test chat message sending specifically"""
        print("\n=== Testing Chat Message Sending (User Reported Issue) ===")
        
        if not self.admin_token:
            print("⚠️  Skipping chat message sending test - no admin token")
            return
        
        # Use admin token for testing
        original_token = self.auth_token
        self.auth_token = self.admin_token
        
        # Test send global message with realistic content
        message_data = {
            "content": "Greetings fellow rulers! Our kingdom stands strong and ready for alliance."
        }
        
        success, data, status = await self.make_request("POST", "/chat/global", message_data, use_auth=True)
        self.log_test(
            "Send Global Message (POST /api/chat/global)",
            success and status == 200,
            f"Status: {status}, Message sent: {data.get('success', False) if isinstance(data, dict) else 'error'}, Response: {data}"
        )
        
        # Test send private message
        private_message_data = {
            "receiver": "admin",
            "content": "Greetings, mighty ruler! I seek to establish diplomatic relations."
        }
        
        success, data, status = await self.make_request("POST", "/chat/private", private_message_data, use_auth=True)
        self.log_test(
            "Send Private Message (POST /api/chat/private)",
            success and status == 200,
            f"Status: {status}, Message sent: {data.get('success', False) if isinstance(data, dict) else 'error'}, Response: {data}"
        )
        
        # Restore original token
        self.auth_token = original_token
    
    async def test_trading_system(self):
        """Test trading system endpoints"""
        print("\n=== Testing Trading System (User Reported Issue) ===")
        
        if not self.admin_token:
            print("⚠️  Skipping trading system test - no admin token")
            return
        
        # Use admin token for testing
        original_token = self.auth_token
        self.auth_token = self.admin_token
        
        # Test create trade offer
        trade_data = {
            "offering": {"gold": 100, "wood": 50},
            "requesting": {"stone": 75, "food": 25},
            "duration": 3600
        }
        
        success, data, status = await self.make_request("POST", "/diplomacy/trade/create", trade_data, use_auth=True)
        self.log_test(
            "Create Trade Offer (POST /api/diplomacy/trade/create)",
            success and status == 200,
            f"Status: {status}, Trade created: {data.get('success', False) if isinstance(data, dict) else 'error'}, Response: {data}"
        )
        
        # Test get trade offers
        success, data, status = await self.make_request("GET", "/diplomacy/trade/offers", use_auth=True)
        self.log_test(
            "Get Trade Offers (GET /api/diplomacy/trade/offers)",
            success and status == 200,
            f"Status: {status}, Offers count: {len(data.get('offers', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # Test get my trade offers
        success, data, status = await self.make_request("GET", "/diplomacy/trade/my-offers", use_auth=True)
        self.log_test(
            "Get My Trade Offers (GET /api/diplomacy/trade/my-offers)",
            success and status == 200,
            f"Status: {status}, My offers count: {len(data.get('offers', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # Restore original token
        self.auth_token = original_token
    
    async def test_alliance_system(self):
        """Test alliance creation and management"""
        print("\n=== Testing Alliance System (User Reported Issue) ===")
        
        if not self.admin_token:
            print("⚠️  Skipping alliance system test - no admin token")
            return
        
        # Use admin token for testing
        original_token = self.auth_token
        self.auth_token = self.admin_token
        
        # Test create alliance
        alliance_data = {
            "name": "Test Warriors Alliance",
            "description": "A mighty alliance of brave warriors seeking glory and conquest!"
        }
        
        success, data, status = await self.make_request("POST", "/diplomacy/alliance/create", alliance_data, use_auth=True)
        self.log_test(
            "Create Alliance (POST /api/diplomacy/alliance/create)",
            success and status == 200,
            f"Status: {status}, Alliance created: {data.get('success', False) if isinstance(data, dict) else 'error'}, Response: {data}"
        )
        
        # Test get alliance list
        success, data, status = await self.make_request("GET", "/diplomacy/alliance/list")
        self.log_test(
            "Get Alliance List (GET /api/diplomacy/alliance/list)",
            success and status == 200,
            f"Status: {status}, Alliances count: {len(data.get('alliances', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # Test get my alliance
        success, data, status = await self.make_request("GET", "/diplomacy/alliance/my", use_auth=True)
        self.log_test(
            "Get My Alliance (GET /api/diplomacy/alliance/my)",
            success and status == 200,
            f"Status: {status}, My alliance: {data.get('alliance', {}).get('name', 'None') if isinstance(data, dict) else 'error'}"
        )
        
        # Test alliance map
        success, data, status = await self.make_request("GET", "/diplomacy/alliance/map")
        self.log_test(
            "Get Alliance Map (GET /api/diplomacy/alliance/map)",
            success and status == 200,
            f"Status: {status}, Map alliances: {len(data.get('alliances', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # Test get alliance invites
        success, data, status = await self.make_request("GET", "/diplomacy/alliance/invites", use_auth=True)
        self.log_test(
            "Get Alliance Invites (GET /api/diplomacy/alliance/invites)",
            success and status == 200,
            f"Status: {status}, Invites count: {len(data.get('invites', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # Restore original token
        self.auth_token = original_token
    
    async def test_profile_endpoints(self):
        """Test profile GET and PUT endpoints specifically"""
        print("\n=== Testing Profile Endpoints (User Reported Issue) ===")
        
        if not self.admin_token:
            print("⚠️  Skipping profile endpoints test - no admin token")
            return
        
        # Use admin token for testing
        original_token = self.auth_token
        self.auth_token = self.admin_token
        
        # Test GET profile
        success, data, status = await self.make_request("GET", "/game/player/profile", use_auth=True)
        self.log_test(
            "Get Player Profile (GET /api/game/player/profile)",
            success and status == 200,
            f"Status: {status}, Kingdom: {data.get('profile', {}).get('kingdomName', 'unknown') if isinstance(data, dict) else 'error'}"
        )
        
        # Test PUT profile update
        profile_update = {
            "username": "admin",  # Required field
            "bio": "A mighty ruler testing the kingdom's systems",
            "motto": "Testing brings strength and glory!"
        }
        
        success, data, status = await self.make_request("PUT", "/game/player/profile", profile_update, use_auth=True)
        self.log_test(
            "Update Player Profile (PUT /api/game/player/profile)",
            success and status == 200,
            f"Status: {status}, Update success: {data.get('success', False) if isinstance(data, dict) else 'error'}, Response: {data}"
        )
        
        # Restore original token
        self.auth_token = original_token
    
    async def test_shop_system(self):
        """Test shop system endpoints (NEW)"""
        print("\n=== Testing Shop System (NEW) ===")
        
        if not self.admin_token:
            print("⚠️  Skipping shop system test - no admin token")
            return
        
        # Use admin token for testing
        original_token = self.auth_token
        self.auth_token = self.admin_token
        
        # Test get shop items
        success, data, status = await self.make_request("GET", "/game/shop/items")
        self.log_test(
            "Get Shop Items (GET /api/game/shop/items)",
            success and status == 200,
            f"Status: {status}, Items count: {len(data.get('items', [])) if isinstance(data, dict) else 'error'}, Response: {data}"
        )
        
        # Test buy shop item - Resource Pack
        if success and isinstance(data, dict) and data.get('items'):
            # Find resource pack item (check both possible IDs)
            resource_pack = next((item for item in data['items'] if item['id'] in ['resource_pack', 'resourcePack']), None)
            if resource_pack:
                purchase_data = {"quantity": 1}
                
                buy_success, buy_response, buy_status = await self.make_request(
                    "POST", f"/game/shop/buy/{resource_pack['id']}", purchase_data, use_auth=True
                )
                
                self.log_test(
                    f"Buy Resource Pack (POST /api/game/shop/buy/{resource_pack['id']})",
                    buy_success and buy_status == 200,
                    f"Status: {buy_status}, Purchase success: {buy_response.get('success', False) if isinstance(buy_response, dict) else 'error'}, Response: {buy_response}"
                )
        
        # Test buy shop item - Army Boost
        if success and isinstance(data, dict) and data.get('items'):
            # Find army boost item (check both possible IDs)
            army_boost = next((item for item in data['items'] if item['id'] in ['army_boost', 'armyBoost']), None)
            if army_boost:
                purchase_data = {"quantity": 1}
                
                buy_success, buy_response, buy_status = await self.make_request(
                    "POST", f"/game/shop/buy/{army_boost['id']}", purchase_data, use_auth=True
                )
                
                self.log_test(
                    f"Buy Army Boost (POST /api/game/shop/buy/{army_boost['id']})",
                    buy_success and buy_status == 200,
                    f"Status: {buy_status}, Purchase success: {buy_response.get('success', False) if isinstance(buy_response, dict) else 'error'}, Response: {buy_response}"
                )
        
        # Test get purchase history
        success, data, status = await self.make_request("GET", "/game/shop/purchases", use_auth=True)
        self.log_test(
            "Get Purchase History (GET /api/game/shop/purchases)",
            success and status == 200,
            f"Status: {status}, Purchases count: {len(data.get('purchases', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # Test get player inventory
        success, data, status = await self.make_request("GET", "/game/shop/inventory", use_auth=True)
        self.log_test(
            "Get Player Inventory (GET /api/game/shop/inventory)",
            success and status == 200,
            f"Status: {status}, Inventory items: {data.get('inventory', {}) if isinstance(data, dict) else 'error'}"
        )
        
        # Restore original token
        self.auth_token = original_token
    
    async def test_alliance_map_system(self):
        """Test alliance map system specifically (User Requested Feature)"""
        print("\n=== Testing Alliance Map System (User Requested Feature) ===")
        
        # Test alliance map endpoint
        success, data, status = await self.make_request("GET", "/diplomacy/alliance/map")
        self.log_test(
            "Get Alliance Map (GET /api/diplomacy/alliance/map)",
            success and status == 200,
            f"Status: {status}, Map alliances: {len(data.get('alliances', [])) if isinstance(data, dict) else 'error'}, Response: {data}"
        )
        
        # Check if alliance map has proper blazons for 10+ member alliances
        if success and isinstance(data, dict):
            alliances = data.get('alliances', [])
            blazon_alliances = [a for a in alliances if a.get('memberCount', 0) >= 10]
            
            self.log_test(
                "Alliance Map Blazons for 10+ Members",
                len(blazon_alliances) > 0,
                f"Alliances with 10+ members showing blazons: {len(blazon_alliances)}, Total map alliances: {len(alliances)}"
            )
            
            # Check blazon data structure
            if blazon_alliances:
                first_alliance = blazon_alliances[0]
                has_flag = 'flag' in first_alliance and isinstance(first_alliance['flag'], dict)
                has_coordinates = 'coordinates' in first_alliance and isinstance(first_alliance['coordinates'], dict)
                
                self.log_test(
                    "Alliance Blazon Data Structure",
                    has_flag and has_coordinates,
                    f"Flag data present: {has_flag}, Coordinates present: {has_coordinates}, Sample: {first_alliance.get('flag', {})}"
                )
    
    async def test_new_admin_features(self):
        """Test new admin features specifically (User Requested Features)"""
        print("\n=== Testing New Admin Features (User Requested Features) ===")
        
        if not self.admin_token:
            print("⚠️  Skipping new admin features test - no admin token")
            return
        
        # Use admin token for testing
        original_token = self.auth_token
        self.auth_token = self.admin_token
        
        # Test broadcast message
        broadcast_data = {
            "content": "Welcome to Medieval Empires! Server maintenance completed successfully."
        }
        
        success, data, status = await self.make_request("POST", "/admin/broadcast-message", broadcast_data, use_auth=True)
        self.log_test(
            "Admin Broadcast Message (POST /api/admin/broadcast-message)",
            success and status == 200,
            f"Status: {status}, Broadcast sent: {data.get('success', False) if isinstance(data, dict) else 'error'}, Response: {data}"
        )
        
        # Test reset player resources
        reset_data = {
            "username": "admin"  # Reset admin's own resources for testing
        }
        
        success, data, status = await self.make_request("POST", "/admin/reset-player-resources", reset_data, use_auth=True)
        self.log_test(
            "Admin Reset Player Resources (POST /api/admin/reset-player-resources)",
            success and status == 200,
            f"Status: {status}, Reset success: {data.get('success', False) if isinstance(data, dict) else 'error'}, Response: {data}"
        )
        
        # Test get server logs
        success, data, status = await self.make_request("GET", "/admin/server-logs", use_auth=True)
        self.log_test(
            "Admin Get Server Logs (GET /api/admin/server-logs)",
            success and status == 200,
            f"Status: {status}, Logs count: {len(data.get('logs', [])) if isinstance(data, dict) else 'error'}, Response: {data}"
        )
        
        # Restore original token
        self.auth_token = original_token
    
    async def test_construction_queue_verification(self):
        """Verify construction queue system is working correctly (User Reported Issue)"""
        print("\n=== Verifying Construction Queue System (User Reported Issue) ===")
        
        if not self.admin_token:
            print("⚠️  Skipping construction queue verification - no admin token")
            return
        
        # Use admin token for testing
        original_token = self.auth_token
        self.auth_token = self.admin_token
        
        # Test GET construction queue
        success, data, status = await self.make_request("GET", "/game/construction/queue", use_auth=True)
        self.log_test(
            "Verify Construction Queue GET (GET /api/game/construction/queue)",
            success and status == 200,
            f"Status: {status}, Queue items: {len(data.get('queue', [])) if isinstance(data, dict) else 'error'}, Response: {data}"
        )
        
        # Test POST building upgrade
        if success and isinstance(data, dict):
            # Get player buildings first
            buildings_success, buildings_data, buildings_status = await self.make_request("GET", "/game/player/buildings", use_auth=True)
            
            if buildings_success and isinstance(buildings_data, dict):
                buildings = buildings_data.get('buildings', [])
                if buildings:
                    # Try to upgrade first building that's not already upgrading
                    for building in buildings:
                        if not building.get('isUpgrading', False):
                            upgrade_data = {"buildingId": building.get("id")}
                            
                            upgrade_success, upgrade_response, upgrade_status = await self.make_request(
                                "POST", "/game/buildings/upgrade", upgrade_data, use_auth=True
                            )
                            
                            self.log_test(
                                "Verify Building Upgrade POST (POST /api/game/buildings/upgrade)",
                                upgrade_success and upgrade_status == 200,
                                f"Status: {upgrade_status}, Success: {upgrade_response.get('success', False) if isinstance(upgrade_response, dict) else 'error'}, Building: {building.get('name', 'unknown')}, Response: {upgrade_response}"
                            )
                            break
        
        # Restore original token
        self.auth_token = original_token
    
    async def test_overall_system_health(self):
        """Test overall system health - verify all previously working systems are still functional"""
        print("\n=== Testing Overall System Health (Previously Working Systems) ===")
        
        if not self.admin_token:
            print("⚠️  Skipping system health test - no admin token")
            return
        
        # Use admin token for comprehensive testing
        original_token = self.auth_token
        self.auth_token = self.admin_token
        
        # Test chat system
        chat_message = {
            "content": "System health check - chat functionality verified!"
        }
        success, data, status = await self.make_request("POST", "/chat/global", chat_message, use_auth=True)
        self.log_test(
            "System Health - Chat System",
            success and status == 200,
            f"Chat working: {success}, Status: {status}"
        )
        
        # Test trading system
        trade_offer = {
            "offering": {"gold": 50, "wood": 25},
            "requesting": {"stone": 30, "food": 20},
            "duration": 1800
        }
        success, data, status = await self.make_request("POST", "/diplomacy/trade/create", trade_offer, use_auth=True)
        self.log_test(
            "System Health - Trading System",
            success and status == 200,
            f"Trading working: {success}, Status: {status}"
        )
        
        # Test alliance creation
        alliance_data = {
            "name": f"Health Check Alliance {datetime.now().strftime('%H%M%S')}",
            "description": "System health verification alliance"
        }
        success, data, status = await self.make_request("POST", "/diplomacy/alliance/create", alliance_data, use_auth=True)
        self.log_test(
            "System Health - Alliance Creation",
            success and status == 200,
            f"Alliance creation working: {success}, Status: {status}"
        )
        
        # Test shop system
        success, data, status = await self.make_request("GET", "/game/shop/items")
        self.log_test(
            "System Health - Shop System",
            success and status == 200,
            f"Shop working: {success}, Status: {status}, Items: {len(data.get('items', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # Restore original token
        self.auth_token = original_token

    async def run_all_tests(self):
        """Run all test suites"""
        print("🏰 Medieval Empires Backend API Test Suite")
        print(f"🔗 Testing API at: {API_URL}")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run all test suites
        await self.test_health_endpoints()
        await self.test_authentication_system()
        await self.test_game_features()
        await self.test_chat_system()
        await self.test_admin_functions()
        await self.test_empire_bonuses()
        await self.test_resource_generation()
        await self.test_army_recruitment()
        
        # Run specific tests for user-reported issues
        await self.test_construction_queue_system()
        await self.test_chat_message_sending()
        await self.test_trading_system()
        await self.test_alliance_system()
        await self.test_profile_endpoints()
        
        # Run new shop system tests
        await self.test_shop_system()
        
        # Run final comprehensive tests (User Requested Features)
        await self.test_alliance_map_system()
        await self.test_new_admin_features()
        await self.test_construction_queue_verification()
        await self.test_overall_system_health()
        
        # Print summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print("🏰 TEST SUMMARY")
        print("=" * 60)
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        print("\n🏰 Medieval Empires Backend Testing Complete!")
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": passed_tests/total_tests*100,
            "duration": duration,
            "results": self.test_results
        }

async def main():
    """Main test runner"""
    async with MedievalEmpiresAPITester() as tester:
        results = await tester.run_all_tests()
        
        # Exit with error code if tests failed
        if results['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())