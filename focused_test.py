#!/usr/bin/env python3
"""
Focused test for the 3 critical endpoints that were failing with ObjectId and datetime serialization errors:
1. Chat message sending (POST /api/chat/global)
2. Trade offer creation (POST /api/diplomacy/trade/create)
3. Alliance creation (POST /api/diplomacy/alliance/create)
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

class FocusedAPITester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: any = None):
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
    
    async def make_request(self, method: str, endpoint: str, data: dict = None, 
                          headers: dict = None, use_auth: bool = False) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        try:
            url = f"{API_URL}{endpoint}"
            request_headers = headers or {}
            
            if use_auth and self.admin_token:
                request_headers["Authorization"] = f"Bearer {self.admin_token}"
            
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
    
    async def login_admin(self):
        """Login as admin to get authentication token"""
        print("\n=== Admin Authentication ===")
        
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
            return True
        return False
    
    async def test_chat_message_sending(self):
        """Test chat message sending (POST /api/chat/global) - Critical Issue #1"""
        print("\n=== Testing Chat Message Sending (Critical Issue #1) ===")
        
        if not self.admin_token:
            print("⚠️  Skipping chat message test - no admin token")
            return
        
        # Test send global message with realistic content
        message_data = {
            "content": "Greetings fellow rulers! Our kingdom stands strong and ready for alliance."
        }
        
        success, data, status = await self.make_request("POST", "/chat/global", message_data, use_auth=True)
        
        # Check for ObjectId serialization issues
        serialization_ok = True
        if isinstance(data, dict):
            # Check if response contains proper string IDs and no ObjectId objects
            message_id = data.get('message_id')
            if message_id and isinstance(message_id, str):
                serialization_ok = True
            elif message_id and not isinstance(message_id, str):
                serialization_ok = False
        
        self.log_test(
            "Send Global Message (POST /api/chat/global)",
            success and status == 200 and serialization_ok,
            f"Status: {status}, Success: {data.get('success', False) if isinstance(data, dict) else 'error'}, Serialization OK: {serialization_ok}, Response: {data}"
        )
        
        # Verify message was actually sent by getting recent messages
        success2, data2, status2 = await self.make_request("GET", "/chat/global")
        
        message_found = False
        if success2 and isinstance(data2, dict):
            messages = data2.get('messages', [])
            for msg in messages:
                if msg.get('content') == message_data['content']:
                    message_found = True
                    break
        
        self.log_test(
            "Verify Message Sent (GET /api/chat/global)",
            success2 and status2 == 200 and message_found,
            f"Status: {status2}, Message found in chat: {message_found}"
        )
    
    async def test_trade_offer_creation(self):
        """Test trade offer creation (POST /api/diplomacy/trade/create) - Critical Issue #2"""
        print("\n=== Testing Trade Offer Creation (Critical Issue #2) ===")
        
        if not self.admin_token:
            print("⚠️  Skipping trade offer test - no admin token")
            return
        
        # Test create trade offer
        trade_data = {
            "offering": {"gold": 100, "wood": 50},
            "requesting": {"stone": 75, "food": 25},
            "duration": 3600
        }
        
        success, data, status = await self.make_request("POST", "/diplomacy/trade/create", trade_data, use_auth=True)
        
        # Check for ObjectId and datetime serialization issues
        serialization_ok = True
        if isinstance(data, dict) and data.get('trade_offer'):
            trade_offer = data['trade_offer']
            
            # Check ID is string
            if 'id' in trade_offer and not isinstance(trade_offer['id'], str):
                serialization_ok = False
            
            # Check dates are ISO format strings
            for date_field in ['createdAt', 'expiresAt']:
                if date_field in trade_offer:
                    date_val = trade_offer[date_field]
                    if not isinstance(date_val, str):
                        serialization_ok = False
                    else:
                        # Try to parse ISO format
                        try:
                            datetime.fromisoformat(date_val.replace('Z', '+00:00'))
                        except:
                            serialization_ok = False
        
        self.log_test(
            "Create Trade Offer (POST /api/diplomacy/trade/create)",
            success and status == 200 and serialization_ok,
            f"Status: {status}, Success: {data.get('success', False) if isinstance(data, dict) else 'error'}, Serialization OK: {serialization_ok}, Response: {data}"
        )
        
        # Verify trade offer was created by getting trade offers
        success2, data2, status2 = await self.make_request("GET", "/diplomacy/trade/my-offers", use_auth=True)
        
        trade_found = False
        if success2 and isinstance(data2, dict):
            offers = data2.get('offers', [])
            for offer in offers:
                if (offer.get('offering', {}).get('gold') == 100 and 
                    offer.get('requesting', {}).get('stone') == 75):
                    trade_found = True
                    break
        
        self.log_test(
            "Verify Trade Offer Created (GET /api/diplomacy/trade/my-offers)",
            success2 and status2 == 200 and trade_found,
            f"Status: {status2}, Trade offer found: {trade_found}"
        )
    
    async def test_alliance_creation(self):
        """Test alliance creation (POST /api/diplomacy/alliance/create) - Critical Issue #3"""
        print("\n=== Testing Alliance Creation (Critical Issue #3) ===")
        
        if not self.admin_token:
            print("⚠️  Skipping alliance creation test - no admin token")
            return
        
        # Test create alliance
        alliance_data = {
            "name": "Test Warriors Alliance",
            "description": "A mighty alliance of brave warriors seeking glory and conquest!"
        }
        
        success, data, status = await self.make_request("POST", "/diplomacy/alliance/create", alliance_data, use_auth=True)
        
        # Check for ObjectId and datetime serialization issues
        serialization_ok = True
        if isinstance(data, dict) and data.get('alliance'):
            alliance = data['alliance']
            
            # Check ID is string
            if 'id' in alliance and not isinstance(alliance['id'], str):
                serialization_ok = False
            
            # Check dates are ISO format strings
            if 'createdAt' in alliance:
                date_val = alliance['createdAt']
                if not isinstance(date_val, str):
                    serialization_ok = False
                else:
                    # Try to parse ISO format
                    try:
                        datetime.fromisoformat(date_val.replace('Z', '+00:00'))
                    except:
                        serialization_ok = False
        
        self.log_test(
            "Create Alliance (POST /api/diplomacy/alliance/create)",
            success and status == 200 and serialization_ok,
            f"Status: {status}, Success: {data.get('success', False) if isinstance(data, dict) else 'error'}, Serialization OK: {serialization_ok}, Response: {data}"
        )
        
        # Verify alliance was created by getting alliance list
        success2, data2, status2 = await self.make_request("GET", "/diplomacy/alliance/list")
        
        alliance_found = False
        if success2 and isinstance(data2, dict):
            alliances = data2.get('alliances', [])
            for alliance in alliances:
                if alliance.get('name') == alliance_data['name']:
                    alliance_found = True
                    break
        
        self.log_test(
            "Verify Alliance Created (GET /api/diplomacy/alliance/list)",
            success2 and status2 == 200 and alliance_found,
            f"Status: {status2}, Alliance found: {alliance_found}"
        )
        
        # Test getting my alliance
        success3, data3, status3 = await self.make_request("GET", "/diplomacy/alliance/my", use_auth=True)
        
        my_alliance_ok = False
        if success3 and isinstance(data3, dict):
            my_alliance = data3.get('alliance')
            if my_alliance and my_alliance.get('name') == alliance_data['name']:
                my_alliance_ok = True
        
        self.log_test(
            "Get My Alliance (GET /api/diplomacy/alliance/my)",
            success3 and status3 == 200 and my_alliance_ok,
            f"Status: {status3}, My alliance correct: {my_alliance_ok}"
        )
    
    async def run_focused_tests(self):
        """Run the focused tests for the 3 critical endpoints"""
        print("🏰 Medieval Empires - Focused Critical Endpoint Tests")
        print(f"🔗 Testing API at: {API_URL}")
        print("=" * 60)
        print("Testing the 3 critical endpoints that were failing with ObjectId and datetime serialization errors:")
        print("1. Chat message sending (POST /api/chat/global)")
        print("2. Trade offer creation (POST /api/diplomacy/trade/create)")
        print("3. Alliance creation (POST /api/diplomacy/alliance/create)")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Login as admin first
        if not await self.login_admin():
            print("❌ Failed to login as admin - cannot proceed with tests")
            return
        
        # Run the 3 critical tests
        await self.test_chat_message_sending()
        await self.test_trade_offer_creation()
        await self.test_alliance_creation()
        
        # Print summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print("🏰 FOCUSED TEST SUMMARY")
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
        else:
            print("\n✅ ALL CRITICAL ENDPOINTS WORKING!")
            print("ObjectId and datetime serialization issues have been resolved.")
        
        print("\n🏰 Focused Testing Complete!")
        
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
    async with FocusedAPITester() as tester:
        results = await tester.run_focused_tests()
        return results

if __name__ == "__main__":
    asyncio.run(main())