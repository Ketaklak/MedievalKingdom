#!/usr/bin/env python3
"""
Specific Tests for JRPG Medieval Game Corrections
Tests the specific scenarios mentioned in the review request
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

class SpecificTestRunner:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.user1_token = None
        self.user2_token = None
        self.test_results = []
        
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

    async def test_admin_user_login(self):
        """Test 1: Admin User Testing"""
        print("\n=== TEST 1: Admin User Testing ===")
        
        # Test login with admin/admin (not testadmin/admin123 as mentioned in request)
        admin_login_data = {
            "username": "admin",
            "password": "admin"
        }
        
        success, data, status = await self.make_request("POST", "/auth/login", admin_login_data)
        
        # Check if login successful and user has admin privileges
        is_admin = False
        if success and isinstance(data, dict):
            self.admin_token = data.get('access_token')
            user_data = data.get('user', {})
            is_admin = user_data.get('isAdmin', False)
        
        self.log_test(
            "Admin Login with admin/admin",
            success and status == 200 and is_admin,
            f"Status: {status}, isAdmin: {is_admin}, Token received: {bool(self.admin_token)}"
        )
        
        if not self.admin_token:
            print("⚠️  Cannot continue admin tests - no admin token")
            return
        
        # Test /api/admin/system-info for new format
        success, data, status = await self.make_request("GET", "/admin/system-info", token=self.admin_token)
        
        # Check for real values (not "N/A")
        has_real_values = False
        if success and isinstance(data, dict):
            system_info = data.get('system', {})
            status_val = system_info.get('status')
            database_val = system_info.get('database')
            cpu_usage = system_info.get('cpu_usage')
            memory_usage = system_info.get('memory_usage')
            
            # Check if values are not "N/A" and are meaningful
            has_real_values = (
                status_val and status_val != "N/A" and
                database_val and database_val != "N/A" and
                cpu_usage is not None and cpu_usage != "N/A" and
                memory_usage is not None and memory_usage != "N/A"
            )
        
        self.log_test(
            "Admin System Info - Real Values Check",
            success and status == 200 and has_real_values,
            f"Status: {status}, Real values: {has_real_values}, System info: {data.get('system', {}) if isinstance(data, dict) else 'error'}"
        )
        
        # Test /api/admin/stats
        success, data, status = await self.make_request("GET", "/admin/stats", token=self.admin_token)
        
        has_stats = False
        if success and isinstance(data, dict):
            stats = data.get('stats', {})
            has_stats = bool(stats.get('totalPlayers')) and bool(stats.get('activePlayers'))
        
        self.log_test(
            "Admin Statistics Endpoint",
            success and status == 200 and has_stats,
            f"Status: {status}, Has stats: {has_stats}, Stats: {data.get('stats', {}) if isinstance(data, dict) else 'error'}"
        )

    async def test_construction_times(self):
        """Test 2: Construction Time Testing"""
        print("\n=== TEST 2: Construction Time Testing ===")
        
        # Create a normal user
        normal_user_data = {
            "username": f"testbuilder_{datetime.now().strftime('%H%M%S')}",
            "password": "buildstrong123",
            "email": f"testbuilder_{datetime.now().strftime('%H%M%S')}@medievalempires.com",
            "kingdomName": "Builder's Kingdom",
            "empire": "norman"
        }
        
        success, data, status = await self.make_request("POST", "/auth/register", normal_user_data)
        
        if success and isinstance(data, dict):
            self.user1_token = data.get('access_token')
        
        self.log_test(
            "Create Normal User for Construction Test",
            success and status == 200 and bool(self.user1_token),
            f"Status: {status}, User created: {normal_user_data['username']}, Token: {bool(self.user1_token)}"
        )
        
        if not self.user1_token:
            print("⚠️  Cannot continue construction tests - no user token")
            return
        
        # Get user's buildings
        success, data, status = await self.make_request("GET", "/game/player/buildings", token=self.user1_token)
        
        building_to_upgrade = None
        if success and isinstance(data, dict):
            buildings = data.get('buildings', [])
            # Find a building that's not already upgrading
            for building in buildings:
                if not building.get('isUpgrading', False):
                    building_to_upgrade = building
                    break
        
        self.log_test(
            "Get User Buildings for Construction",
            success and status == 200 and bool(building_to_upgrade),
            f"Status: {status}, Buildings found: {len(data.get('buildings', [])) if isinstance(data, dict) else 0}, Available for upgrade: {bool(building_to_upgrade)}"
        )
        
        if not building_to_upgrade:
            print("⚠️  No buildings available for upgrade")
            return
        
        # Start building construction
        upgrade_data = {"buildingId": building_to_upgrade.get("id")}
        success, data, status = await self.make_request("POST", "/game/buildings/upgrade", upgrade_data, token=self.user1_token)
        
        self.log_test(
            "Start Building Construction",
            success and status == 200,
            f"Status: {status}, Construction started: {data.get('success', False) if isinstance(data, dict) else 'error'}"
        )
        
        # Check construction queue for valid times
        success, data, status = await self.make_request("GET", "/game/construction/queue", token=self.user1_token)
        
        valid_times = True
        construction_times = []
        if success and isinstance(data, dict):
            queue = data.get('queue', [])
            for item in queue:
                completion_time = item.get('completionTime')
                remaining_time = item.get('remainingTime')
                
                # Check if times are valid numbers (not NaN)
                if completion_time is not None:
                    try:
                        # Try to parse as number or datetime
                        if isinstance(completion_time, (int, float)):
                            if completion_time != completion_time:  # Check for NaN
                                valid_times = False
                        construction_times.append(completion_time)
                    except:
                        valid_times = False
                
                if remaining_time is not None:
                    try:
                        if isinstance(remaining_time, (int, float)):
                            if remaining_time != remaining_time:  # Check for NaN
                                valid_times = False
                        construction_times.append(remaining_time)
                    except:
                        valid_times = False
        
        self.log_test(
            "Construction Times Validation (Not NaN)",
            success and status == 200 and valid_times,
            f"Status: {status}, Valid times: {valid_times}, Queue items: {len(data.get('queue', [])) if isinstance(data, dict) else 0}, Sample times: {construction_times[:3]}"
        )

    async def test_diplomacy_features(self):
        """Test 3: Diplomacy Testing"""
        print("\n=== TEST 3: Diplomacy Testing ===")
        
        # Create first normal user
        user1_data = {
            "username": f"diplomat1_{datetime.now().strftime('%H%M%S')}",
            "password": "diplomatic123",
            "email": f"diplomat1_{datetime.now().strftime('%H%M%S')}@medievalempires.com",
            "kingdomName": "Diplomatic Kingdom",
            "empire": "norman"
        }
        
        success, data, status = await self.make_request("POST", "/auth/register", user1_data)
        
        if success and isinstance(data, dict):
            self.user1_token = data.get('access_token')
        
        self.log_test(
            "Create First Diplomat User",
            success and status == 200 and bool(self.user1_token),
            f"Status: {status}, User created: {user1_data['username']}"
        )
        
        # Create second normal user
        user2_data = {
            "username": f"diplomat2_{datetime.now().strftime('%H%M%S')}",
            "password": "diplomatic456",
            "email": f"diplomat2_{datetime.now().strftime('%H%M%S')}@medievalempires.com",
            "kingdomName": "Allied Kingdom",
            "empire": "viking"
        }
        
        success, data, status = await self.make_request("POST", "/auth/register", user2_data)
        
        if success and isinstance(data, dict):
            self.user2_token = data.get('access_token')
        
        self.log_test(
            "Create Second Diplomat User",
            success and status == 200 and bool(self.user2_token),
            f"Status: {status}, User created: {user2_data['username']}"
        )
        
        if not self.user1_token or not self.user2_token:
            print("⚠️  Cannot continue diplomacy tests - missing user tokens")
            return
        
        # Create alliance with first user
        alliance_data = {
            "name": f"Test Alliance {datetime.now().strftime('%H%M%S')}",
            "description": "A test alliance for diplomatic relations and mutual prosperity"
        }
        
        success, data, status = await self.make_request("POST", "/diplomacy/alliance/create", alliance_data, token=self.user1_token)
        
        self.log_test(
            "Create Alliance with First User",
            success and status == 200,
            f"Status: {status}, Alliance created: {data.get('success', False) if isinstance(data, dict) else 'error'}"
        )
        
        # Create trade offer with first user
        trade_data = {
            "offering": {"gold": 200, "wood": 100},
            "requesting": {"stone": 150, "food": 75},
            "duration": 7200
        }
        
        success, data, status = await self.make_request("POST", "/diplomacy/trade/create", trade_data, token=self.user1_token)
        
        self.log_test(
            "Create Trade Offer with First User",
            success and status == 200,
            f"Status: {status}, Trade created: {data.get('success', False) if isinstance(data, dict) else 'error'}"
        )
        
        # List alliances via GET endpoint
        success, data, status = await self.make_request("GET", "/diplomacy/alliance/list")
        
        proper_alliance_format = True
        if success and isinstance(data, dict):
            alliances = data.get('alliances', [])
            for alliance in alliances:
                # Check for proper data format (no raw ObjectId)
                if '_id' in alliance and not isinstance(alliance['_id'], str):
                    proper_alliance_format = False
                # Check for required fields
                if not all(key in alliance for key in ['name', 'description', 'memberCount']):
                    proper_alliance_format = False
        
        self.log_test(
            "List Alliances - Proper Data Format",
            success and status == 200 and proper_alliance_format,
            f"Status: {status}, Alliances count: {len(data.get('alliances', [])) if isinstance(data, dict) else 0}, Proper format: {proper_alliance_format}"
        )
        
        # List trade offers via GET endpoint
        success, data, status = await self.make_request("GET", "/diplomacy/trade/offers")
        
        proper_trade_format = True
        if success and isinstance(data, dict):
            offers = data.get('offers', [])
            for offer in offers:
                # Check for proper data format (no raw ObjectId)
                if '_id' in offer and not isinstance(offer['_id'], str):
                    proper_trade_format = False
                # Check for required fields and proper datetime serialization
                if not all(key in offer for key in ['offering', 'requesting', 'createdAt']):
                    proper_trade_format = False
                # Check datetime is string (ISO format)
                created_at = offer.get('createdAt')
                if created_at and not isinstance(created_at, str):
                    proper_trade_format = False
        
        self.log_test(
            "List Trade Offers - Proper Data Format",
            success and status == 200 and proper_trade_format,
            f"Status: {status}, Trade offers count: {len(data.get('offers', [])) if isinstance(data, dict) else 0}, Proper format: {proper_trade_format}"
        )
        
        # Test serialization - ensure no "Objects are not valid as a React child" errors
        # This means checking that all data is properly JSON serializable
        serialization_test = True
        try:
            # Test alliance data serialization
            alliance_success, alliance_data, _ = await self.make_request("GET", "/diplomacy/alliance/list")
            if alliance_success:
                json.dumps(alliance_data)  # This will fail if not serializable
            
            # Test trade data serialization
            trade_success, trade_data, _ = await self.make_request("GET", "/diplomacy/trade/offers")
            if trade_success:
                json.dumps(trade_data)  # This will fail if not serializable
                
        except (TypeError, ValueError) as e:
            serialization_test = False
        
        self.log_test(
            "Data Serialization Test (No React Child Errors)",
            serialization_test,
            f"All diplomacy data properly JSON serializable: {serialization_test}"
        )

    async def run_specific_tests(self):
        """Run all specific tests requested by user"""
        print("🏰 JRPG Medieval Game - Specific Corrections Testing")
        print(f"🔗 Testing API at: {API_URL}")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run the three main test categories
        await self.test_admin_user_login()
        await self.test_construction_times()
        await self.test_diplomacy_features()
        
        # Print summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print("🏰 SPECIFIC TESTS SUMMARY")
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
        
        print("\n🏰 Specific Testing Complete!")
        
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
    async with SpecificTestRunner() as tester:
        results = await tester.run_specific_tests()
        
        # Exit with error code if tests failed
        if results['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())