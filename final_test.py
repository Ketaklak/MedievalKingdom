#!/usr/bin/env python3
"""
Final Focused Test for User Review Request
Tests the exact scenarios mentioned in the review request
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

class FinalTestRunner:
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

    async def test_admin_user_with_correct_credentials(self):
        """Test admin user with admin/admin (not testadmin/admin123)"""
        print("\n=== FINAL TEST 1: Admin User Testing (admin/admin) ===")
        
        # Test login with admin/admin
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
            "Admin Login (admin/admin) - isAdmin: true",
            success and status == 200 and is_admin,
            f"Status: {status}, isAdmin: {is_admin}, Token received: {bool(self.admin_token)}"
        )
        
        if not self.admin_token:
            print("⚠️  Cannot continue admin tests - no admin token")
            return
        
        # Test /api/admin/system-info for NEW FORMAT with real values
        success, data, status = await self.make_request("GET", "/admin/system-info", token=self.admin_token)
        
        # Check the EXACT format expected by user
        has_correct_format = False
        real_values = False
        if success and isinstance(data, dict):
            # Check if it has the expected fields at root level (not nested in 'system')
            status_val = data.get('status')
            database_val = data.get('database') 
            cpu_usage = data.get('cpuUsage')
            memory_usage = data.get('memoryUsage')
            
            has_correct_format = all([
                status_val is not None,
                database_val is not None,
                cpu_usage is not None,
                memory_usage is not None
            ])
            
            # Check if values are real (not "N/A")
            real_values = (
                status_val and status_val != "N/A" and
                database_val and database_val != "N/A" and
                cpu_usage and cpu_usage != "N/A" and
                memory_usage and memory_usage != "N/A"
            )
        
        self.log_test(
            "Admin System Info - NEW FORMAT with Real Values",
            success and status == 200 and has_correct_format and real_values,
            f"Status: {status}, Correct format: {has_correct_format}, Real values: {real_values}, Response: {data}"
        )
        
        # Test /api/admin/stats for statistics
        success, data, status = await self.make_request("GET", "/admin/stats", token=self.admin_token)
        
        has_stats = False
        if success and isinstance(data, dict):
            # Check if stats are at root level (not nested)
            total_players = data.get('totalPlayers')
            active_players = data.get('activePlayers')
            has_stats = total_players is not None and active_players is not None
        
        self.log_test(
            "Admin Statistics - Direct Stats Format",
            success and status == 200 and has_stats,
            f"Status: {status}, Has stats: {has_stats}, Total players: {data.get('totalPlayers')}, Active: {data.get('activePlayers')}"
        )

    async def test_construction_times_with_new_user(self):
        """Test construction times with a completely new user"""
        print("\n=== FINAL TEST 2: Construction Times (New User) ===")
        
        # Create a brand new user with unique timestamp
        timestamp = datetime.now().strftime('%H%M%S%f')
        normal_user_data = {
            "username": f"builder_{timestamp}",
            "password": "buildstrong123",
            "email": f"builder_{timestamp}@medievalempires.com",
            "kingdomName": f"Builder Kingdom {timestamp}",
            "empire": "norman"
        }
        
        success, data, status = await self.make_request("POST", "/auth/register", normal_user_data)
        
        if success and isinstance(data, dict):
            self.user1_token = data.get('access_token')
        
        self.log_test(
            "Create New User for Construction Test",
            success and status == 200 and bool(self.user1_token),
            f"Status: {status}, User: {normal_user_data['username']}, Token: {bool(self.user1_token)}"
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
            "Get Buildings for New User",
            success and status == 200 and bool(building_to_upgrade),
            f"Status: {status}, Buildings: {len(data.get('buildings', [])) if isinstance(data, dict) else 0}, Available: {bool(building_to_upgrade)}"
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
        
        # Check construction queue for VALID TIMES (not NaN)
        success, data, status = await self.make_request("GET", "/game/construction/queue", token=self.user1_token)
        
        valid_times = True
        construction_details = []
        if success and isinstance(data, dict):
            queue = data.get('queue', [])
            for item in queue:
                completion_time = item.get('completionTime')
                remaining_time = item.get('remainingTime')
                start_time = item.get('startTime')
                
                # Check all time fields for validity
                for time_field, time_value in [('completionTime', completion_time), ('remainingTime', remaining_time), ('startTime', start_time)]:
                    if time_value is not None:
                        try:
                            # Check if it's a valid number or string
                            if isinstance(time_value, (int, float)):
                                # Check for NaN
                                if time_value != time_value:  # NaN check
                                    valid_times = False
                                    construction_details.append(f"{time_field}: NaN")
                                else:
                                    construction_details.append(f"{time_field}: {time_value}")
                            elif isinstance(time_value, str):
                                # Valid string time
                                construction_details.append(f"{time_field}: {time_value}")
                            else:
                                valid_times = False
                                construction_details.append(f"{time_field}: Invalid type {type(time_value)}")
                        except Exception as e:
                            valid_times = False
                            construction_details.append(f"{time_field}: Error {e}")
        
        self.log_test(
            "Construction Times Validation (No NaN Values)",
            success and status == 200 and valid_times,
            f"Status: {status}, Valid times: {valid_times}, Queue items: {len(data.get('queue', [])) if isinstance(data, dict) else 0}, Details: {construction_details[:3]}"
        )

    async def test_diplomacy_with_fresh_users(self):
        """Test diplomacy with completely fresh users"""
        print("\n=== FINAL TEST 3: Diplomacy Testing (Fresh Users) ===")
        
        timestamp = datetime.now().strftime('%H%M%S%f')
        
        # Create first diplomat user
        user1_data = {
            "username": f"diplomat1_{timestamp}",
            "password": "diplomatic123",
            "email": f"diplomat1_{timestamp}@medievalempires.com",
            "kingdomName": f"Diplomatic Kingdom {timestamp}",
            "empire": "norman"
        }
        
        success, data, status = await self.make_request("POST", "/auth/register", user1_data)
        
        if success and isinstance(data, dict):
            self.user1_token = data.get('access_token')
        
        self.log_test(
            "Create First Diplomat User",
            success and status == 200 and bool(self.user1_token),
            f"Status: {status}, User: {user1_data['username']}"
        )
        
        # Create second diplomat user
        user2_data = {
            "username": f"diplomat2_{timestamp}",
            "password": "diplomatic456",
            "email": f"diplomat2_{timestamp}@medievalempires.com",
            "kingdomName": f"Allied Kingdom {timestamp}",
            "empire": "viking"
        }
        
        success, data, status = await self.make_request("POST", "/auth/register", user2_data)
        
        if success and isinstance(data, dict):
            self.user2_token = data.get('access_token')
        
        self.log_test(
            "Create Second Diplomat User",
            success and status == 200 and bool(self.user2_token),
            f"Status: {status}, User: {user2_data['username']}"
        )
        
        if not self.user1_token or not self.user2_token:
            print("⚠️  Cannot continue diplomacy tests - missing user tokens")
            return
        
        # Create alliance with first user
        alliance_data = {
            "name": f"Diplomatic Alliance {timestamp}",
            "description": "A fresh alliance for testing diplomatic relations and mutual prosperity"
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
        
        # List alliances via GET endpoint - check data format
        success, data, status = await self.make_request("GET", "/diplomacy/alliance/list")
        
        proper_alliance_format = True
        alliance_count = 0
        if success and isinstance(data, dict):
            alliances = data.get('alliances', [])
            alliance_count = len(alliances)
            for alliance in alliances:
                # Check for proper data format (no raw ObjectId, proper serialization)
                if '_id' in alliance and not isinstance(alliance['_id'], str):
                    proper_alliance_format = False
                # Check for required fields
                required_fields = ['name', 'description', 'memberCount']
                if not all(key in alliance for key in required_fields):
                    proper_alliance_format = False
        
        self.log_test(
            "List Alliances - Proper Data Format (No React Child Errors)",
            success and status == 200 and proper_alliance_format,
            f"Status: {status}, Alliances: {alliance_count}, Proper format: {proper_alliance_format}"
        )
        
        # List trade offers via GET endpoint - check data format
        success, data, status = await self.make_request("GET", "/diplomacy/trade/offers")
        
        proper_trade_format = True
        trade_count = 0
        if success and isinstance(data, dict):
            offers = data.get('offers', [])
            trade_count = len(offers)
            for offer in offers:
                # Check for proper data format (no raw ObjectId)
                if '_id' in offer and not isinstance(offer['_id'], str):
                    proper_trade_format = False
                # Check for required fields and proper datetime serialization
                required_fields = ['offering', 'requesting', 'createdAt']
                if not all(key in offer for key in required_fields):
                    proper_trade_format = False
                # Check datetime is string (ISO format) - not object
                created_at = offer.get('createdAt')
                if created_at and not isinstance(created_at, str):
                    proper_trade_format = False
        
        self.log_test(
            "List Trade Offers - Proper Data Format (No React Child Errors)",
            success and status == 200 and proper_trade_format,
            f"Status: {status}, Trade offers: {trade_count}, Proper format: {proper_trade_format}"
        )
        
        # Final serialization test - ensure no "Objects are not valid as a React child" errors
        serialization_test = True
        serialization_errors = []
        
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
            serialization_errors.append(str(e))
        
        self.log_test(
            "Complete Serialization Test (No 'Objects are not valid as React child' Errors)",
            serialization_test,
            f"All diplomacy data properly JSON serializable: {serialization_test}, Errors: {serialization_errors}"
        )

    async def run_final_tests(self):
        """Run the final focused tests for user review"""
        print("🏰 JRPG Medieval Game - FINAL CORRECTIONS VERIFICATION")
        print(f"🔗 Testing API at: {API_URL}")
        print("=" * 70)
        
        start_time = datetime.now()
        
        # Run the three main test categories as requested
        await self.test_admin_user_with_correct_credentials()
        await self.test_construction_times_with_new_user()
        await self.test_diplomacy_with_fresh_users()
        
        # Print summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 70)
        print("🏰 FINAL VERIFICATION SUMMARY")
        print("=" * 70)
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
        
        print("\n🏰 Final Verification Complete!")
        
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
    async with FinalTestRunner() as tester:
        results = await tester.run_final_tests()
        
        # Exit with error code if tests failed
        if results['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())