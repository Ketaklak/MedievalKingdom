#!/usr/bin/env python3
"""
Medieval Empires Diplomacy System Test Suite
Tests diplomacy features as requested by user:
- Trade/Commerce System
- Alliance System  
- Admin Panel
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

class DiplomacyTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.player1_token = None
        self.player2_token = None
        self.admin_token = None
        self.trade_offer_id = None
        
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
                          headers: Dict = None, token: str = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        try:
            url = f"{API_URL}{endpoint}"
            request_headers = headers or {}
            
            if token:
                request_headers["Authorization"] = f"Bearer {token}"
            
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
    
    async def setup_test_accounts(self):
        """Create 2 test accounts (player1, player2) and get admin token"""
        print("\n=== Setting Up Test Accounts ===")
        
        # Create player1 account
        player1_data = {
            "username": "lordarthur",
            "password": "knightofcamelot123",
            "email": "lordarthur@camelot.com",
            "kingdomName": "Camelot Kingdom",
            "empire": "norman"
        }
        
        success, data, status = await self.make_request("POST", "/auth/register", player1_data)
        self.log_test(
            "Create Player1 Account (lordarthur)",
            success and status == 200,
            f"Status: {status}, Username: {data.get('user', {}).get('username', 'unknown') if isinstance(data, dict) else 'error'}"
        )
        
        if success and isinstance(data, dict) and 'access_token' in data:
            self.player1_token = data['access_token']
        
        # Create player2 account
        player2_data = {
            "username": "queenguinevere",
            "password": "royalqueen456",
            "email": "queenguinevere@camelot.com",
            "kingdomName": "Royal Court",
            "empire": "byzantine"
        }
        
        success, data, status = await self.make_request("POST", "/auth/register", player2_data)
        self.log_test(
            "Create Player2 Account (queenguinevere)",
            success and status == 200,
            f"Status: {status}, Username: {data.get('user', {}).get('username', 'unknown') if isinstance(data, dict) else 'error'}"
        )
        
        if success and isinstance(data, dict) and 'access_token' in data:
            self.player2_token = data['access_token']
        
        # Get admin token
        admin_login_data = {
            "username": "admin",
            "password": "admin"
        }
        
        success, data, status = await self.make_request("POST", "/auth/login", admin_login_data)
        self.log_test(
            "Admin Login",
            success and status == 200,
            f"Status: {status}, Admin logged in: {data.get('user', {}).get('isAdmin', False) if isinstance(data, dict) else 'error'}"
        )
        
        if success and isinstance(data, dict) and 'access_token' in data:
            self.admin_token = data['access_token']
    
    async def test_trade_system(self):
        """Test Trade/Commerce System"""
        print("\n=== Testing Trade/Commerce System ===")
        
        if not self.player1_token or not self.player2_token:
            print("⚠️  Skipping trade tests - missing player tokens")
            return
        
        # 1. POST /api/diplomacy/trade/create - Player1 creates trade offer
        trade_data = {
            "offering": {"gold": 500, "wood": 200},
            "requesting": {"stone": 300, "food": 150},
            "duration": 3600
        }
        
        success, data, status = await self.make_request(
            "POST", "/diplomacy/trade/create", trade_data, token=self.player1_token
        )
        self.log_test(
            "POST /api/diplomacy/trade/create - Create Trade Offer",
            success and status == 200,
            f"Status: {status}, Trade created: {data.get('success', False) if isinstance(data, dict) else 'error'}"
        )
        
        # Store trade offer ID for later acceptance
        if success and isinstance(data, dict) and 'offer' in data:
            self.trade_offer_id = data['offer'].get('id')
        
        # 2. GET /api/diplomacy/trade/offers - List all offers
        success, data, status = await self.make_request(
            "GET", "/diplomacy/trade/offers", token=self.player2_token
        )
        self.log_test(
            "GET /api/diplomacy/trade/offers - List All Offers",
            success and status == 200,
            f"Status: {status}, Offers count: {len(data.get('offers', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # 3. GET /api/diplomacy/trade/my-offers - Player1's offers
        success, data, status = await self.make_request(
            "GET", "/diplomacy/trade/my-offers", token=self.player1_token
        )
        self.log_test(
            "GET /api/diplomacy/trade/my-offers - My Trade Offers",
            success and status == 200,
            f"Status: {status}, My offers count: {len(data.get('offers', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # 4. POST /api/diplomacy/trade/accept/{offerId} - Player2 accepts offer
        if self.trade_offer_id:
            success, data, status = await self.make_request(
                "POST", f"/diplomacy/trade/accept/{self.trade_offer_id}", token=self.player2_token
            )
            self.log_test(
                f"POST /api/diplomacy/trade/accept/{self.trade_offer_id} - Accept Trade Offer",
                success and status == 200,
                f"Status: {status}, Trade accepted: {data.get('success', False) if isinstance(data, dict) else 'error'}"
            )
        else:
            self.log_test(
                "POST /api/diplomacy/trade/accept/{offerId} - Accept Trade Offer",
                False,
                "No trade offer ID available to test acceptance"
            )
    
    async def test_alliance_system(self):
        """Test Alliance System"""
        print("\n=== Testing Alliance System ===")
        
        if not self.player1_token:
            print("⚠️  Skipping alliance tests - missing player1 token")
            return
        
        # 1. POST /api/diplomacy/alliance/create - Player1 creates alliance
        alliance_data = {
            "name": "Knights of the Round Table",
            "description": "A noble alliance of brave knights seeking honor and glory in battle!"
        }
        
        success, data, status = await self.make_request(
            "POST", "/diplomacy/alliance/create", alliance_data, token=self.player1_token
        )
        self.log_test(
            "POST /api/diplomacy/alliance/create - Create Alliance",
            success and status == 200,
            f"Status: {status}, Alliance created: {data.get('success', False) if isinstance(data, dict) else 'error'}"
        )
        
        # 2. GET /api/diplomacy/alliance/list - List all alliances
        success, data, status = await self.make_request("GET", "/diplomacy/alliance/list")
        self.log_test(
            "GET /api/diplomacy/alliance/list - List All Alliances",
            success and status == 200,
            f"Status: {status}, Alliances count: {len(data.get('alliances', [])) if isinstance(data, dict) else 'error'}"
        )
        
        # 3. GET /api/diplomacy/alliance/my - Player1's current alliance
        success, data, status = await self.make_request(
            "GET", "/diplomacy/alliance/my", token=self.player1_token
        )
        self.log_test(
            "GET /api/diplomacy/alliance/my - My Current Alliance",
            success and status == 200,
            f"Status: {status}, My alliance: {data.get('alliance', {}).get('name', 'None') if isinstance(data, dict) else 'error'}"
        )
        
        # 4. GET /api/diplomacy/alliance/map - Alliance map
        success, data, status = await self.make_request("GET", "/diplomacy/alliance/map")
        self.log_test(
            "GET /api/diplomacy/alliance/map - Alliance Map",
            success and status == 200,
            f"Status: {status}, Map alliances: {len(data.get('alliances', [])) if isinstance(data, dict) else 'error'}"
        )
    
    async def test_admin_panel(self):
        """Test Admin Panel"""
        print("\n=== Testing Admin Panel ===")
        
        if not self.admin_token:
            print("⚠️  Skipping admin tests - missing admin token")
            return
        
        # 1. GET /api/admin/stats - Server statistics
        success, data, status = await self.make_request(
            "GET", "/admin/stats", token=self.admin_token
        )
        self.log_test(
            "GET /api/admin/stats - Server Statistics",
            success and status == 200,
            f"Status: {status}, Total players: {data.get('stats', {}).get('totalPlayers', 'unknown') if isinstance(data, dict) else 'error'}"
        )
        
        # 2. GET /api/admin/system-info - System information
        success, data, status = await self.make_request(
            "GET", "/admin/system-info", token=self.admin_token
        )
        self.log_test(
            "GET /api/admin/system-info - System Information",
            success and status == 200,
            f"Status: {status}, CPU usage: {data.get('system', {}).get('cpu_usage', 'unknown') if isinstance(data, dict) else 'error'}"
        )
        
        # 3. GET /api/admin/players - Player list
        success, data, status = await self.make_request(
            "GET", "/admin/players", token=self.admin_token
        )
        self.log_test(
            "GET /api/admin/players - Player List",
            success and status == 200,
            f"Status: {status}, Players count: {len(data.get('players', [])) if isinstance(data, dict) else 'error'}"
        )
    
    async def test_data_serialization(self):
        """Test that endpoints return properly serialized data (no ObjectId issues)"""
        print("\n=== Testing Data Serialization ===")
        
        # Test trade offers serialization
        if self.player1_token:
            success, data, status = await self.make_request(
                "GET", "/diplomacy/trade/offers", token=self.player1_token
            )
            
            serialization_ok = True
            error_details = ""
            
            if success and isinstance(data, dict):
                # Check if response can be JSON serialized (no ObjectId issues)
                try:
                    json.dumps(data)
                except Exception as e:
                    serialization_ok = False
                    error_details = f"JSON serialization error: {e}"
            else:
                serialization_ok = False
                error_details = f"Invalid response format: {data}"
            
            self.log_test(
                "Trade Offers Data Serialization",
                serialization_ok,
                f"JSON serializable: {serialization_ok}, {error_details}"
            )
        
        # Test alliance list serialization
        success, data, status = await self.make_request("GET", "/diplomacy/alliance/list")
        
        serialization_ok = True
        error_details = ""
        
        if success and isinstance(data, dict):
            try:
                json.dumps(data)
            except Exception as e:
                serialization_ok = False
                error_details = f"JSON serialization error: {e}"
        else:
            serialization_ok = False
            error_details = f"Invalid response format: {data}"
        
        self.log_test(
            "Alliance List Data Serialization",
            serialization_ok,
            f"JSON serializable: {serialization_ok}, {error_details}"
        )
    
    async def test_error_handling(self):
        """Test error handling for various scenarios"""
        print("\n=== Testing Error Handling ===")
        
        # Test creating trade offer without authentication
        trade_data = {
            "offering": {"gold": 100},
            "requesting": {"stone": 50},
            "duration": 3600
        }
        
        success, data, status = await self.make_request(
            "POST", "/diplomacy/trade/create", trade_data
        )
        self.log_test(
            "Trade Creation Without Auth - Error Handling",
            not success or status == 401,
            f"Status: {status}, Properly rejected unauthorized request: {not success or status == 401}"
        )
        
        # Test creating alliance without authentication
        alliance_data = {
            "name": "Test Alliance",
            "description": "Test description"
        }
        
        success, data, status = await self.make_request(
            "POST", "/diplomacy/alliance/create", alliance_data
        )
        self.log_test(
            "Alliance Creation Without Auth - Error Handling",
            not success or status == 401,
            f"Status: {status}, Properly rejected unauthorized request: {not success or status == 401}"
        )
        
        # Test admin endpoints without admin token
        success, data, status = await self.make_request(
            "GET", "/admin/stats", token=self.player1_token if self.player1_token else None
        )
        self.log_test(
            "Admin Stats Without Admin Auth - Error Handling",
            not success or status in [401, 403],
            f"Status: {status}, Properly rejected non-admin request: {not success or status in [401, 403]}"
        )
    
    async def run_diplomacy_tests(self):
        """Run all diplomacy-focused tests"""
        print("🏰 Medieval Empires Diplomacy System Test Suite")
        print(f"🔗 Testing API at: {API_URL}")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Setup test accounts
        await self.setup_test_accounts()
        
        # Run diplomacy tests
        await self.test_trade_system()
        await self.test_alliance_system()
        await self.test_admin_panel()
        await self.test_data_serialization()
        await self.test_error_handling()
        
        # Print summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print("🏰 DIPLOMACY TEST SUMMARY")
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
        
        print("\n🏰 Diplomacy System Testing Complete!")
        
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
    async with DiplomacyTester() as tester:
        results = await tester.run_diplomacy_tests()
        
        # Exit with error code if tests failed
        if results['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())