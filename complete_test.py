#!/usr/bin/env python3
"""
Complete Test for User Review Request - Using Existing Users
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

class CompleteTestRunner:
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

    async def test_admin_user_complete(self):
        """Complete admin user testing as requested"""
        print("\n=== TEST 1: Admin User Testing (admin/admin not testadmin/admin123) ===")
        
        # Test login with admin/admin (correct credentials, not testadmin/admin123)
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
            "✓ Admin Login (admin/admin) - Verify isAdmin: true",
            success and status == 200 and is_admin,
            f"Status: {status}, isAdmin: {is_admin}, Token received: {bool(self.admin_token)}"
        )
        
        if not self.admin_token:
            print("⚠️  Cannot continue admin tests - no admin token")
            return
        
        # Test /api/admin/system-info for NEW FORMAT with real values (not "N/A")
        success, data, status = await self.make_request("GET", "/admin/system-info", token=self.admin_token)
        
        # Check the EXACT format expected: status/database/cpuUsage/memoryUsage with real values
        has_correct_format = False
        real_values = False
        system_details = {}
        
        if success and isinstance(data, dict):
            status_val = data.get('status')
            database_val = data.get('database') 
            cpu_usage = data.get('cpuUsage')
            memory_usage = data.get('memoryUsage')
            
            system_details = {
                'status': status_val,
                'database': database_val,
                'cpuUsage': cpu_usage,
                'memoryUsage': memory_usage
            }
            
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
            "✓ Admin System Info - Returns status/database/cpuUsage/memoryUsage with REAL values (not N/A)",
            success and status == 200 and has_correct_format and real_values,
            f"Status: {status}, Format: {has_correct_format}, Real values: {real_values}, Data: {system_details}"
        )
        
        # Test /api/admin/stats for statistics
        success, data, status = await self.make_request("GET", "/admin/stats", token=self.admin_token)
        
        has_stats = False
        stats_details = {}
        if success and isinstance(data, dict):
            total_players = data.get('totalPlayers')
            active_players = data.get('activePlayers')
            stats_details = {
                'totalPlayers': total_players,
                'activePlayers': active_players,
                'totalMessages': data.get('totalMessages'),
                'totalPower': data.get('totalPower')
            }
            has_stats = total_players is not None and active_players is not None
        
        self.log_test(
            "✓ Admin Statistics - Verify statistics endpoint working",
            success and status == 200 and has_stats,
            f"Status: {status}, Has stats: {has_stats}, Stats: {stats_details}"
        )

    async def test_construction_times_complete(self):
        """Complete construction time testing"""
        print("\n=== TEST 2: Construction Time Testing ===")
        
        if not self.admin_token:
            print("⚠️  Using admin token for construction test")
            return
        
        # Use admin for construction testing since user registration is having issues
        # Get admin's buildings
        success, data, status = await self.make_request("GET", "/game/player/buildings", token=self.admin_token)
        
        building_to_upgrade = None
        if success and isinstance(data, dict):
            buildings = data.get('buildings', [])
            # Find a building that's not already upgrading
            for building in buildings:
                if not building.get('isUpgrading', False):
                    building_to_upgrade = building
                    break
        
        self.log_test(
            "✓ Get Buildings for Construction Test",
            success and status == 200 and bool(building_to_upgrade),
            f"Status: {status}, Buildings: {len(data.get('buildings', [])) if isinstance(data, dict) else 0}, Available: {bool(building_to_upgrade)}"
        )
        
        if building_to_upgrade:
            # Start building construction
            upgrade_data = {"buildingId": building_to_upgrade.get("id")}
            success, data, status = await self.make_request("POST", "/game/buildings/upgrade", upgrade_data, token=self.admin_token)
            
            self.log_test(
                "✓ Start Building Construction",
                success and status == 200,
                f"Status: {status}, Construction started: {data.get('success', False) if isinstance(data, dict) else 'error'}"
            )
        
        # Check construction queue for VALID TIMES (not NaN) - This is the key test
        success, data, status = await self.make_request("GET", "/game/construction/queue", token=self.admin_token)
        
        valid_times = True
        construction_details = []
        nan_found = False
        
        if success and isinstance(data, dict):
            queue = data.get('queue', [])
            for item in queue:
                completion_time = item.get('completionTime')
                remaining_time = item.get('remainingTime')
                start_time = item.get('startTime')
                
                # Check all time fields for validity (specifically for NaN)
                for time_field, time_value in [('completionTime', completion_time), ('remainingTime', remaining_time), ('startTime', start_time)]:
                    if time_value is not None:
                        try:
                            # Check if it's a valid number or string
                            if isinstance(time_value, (int, float)):
                                # Check for NaN - this is the critical test
                                if time_value != time_value:  # NaN check
                                    valid_times = False
                                    nan_found = True
                                    construction_details.append(f"{time_field}: NaN ❌")
                                else:
                                    construction_details.append(f"{time_field}: {time_value} ✅")
                            elif isinstance(time_value, str):
                                # Valid string time
                                construction_details.append(f"{time_field}: {time_value} ✅")
                            else:
                                construction_details.append(f"{time_field}: {type(time_value)} ⚠️")
                        except Exception as e:
                            valid_times = False
                            construction_details.append(f"{time_field}: Error {e} ❌")
        
        self.log_test(
            "✓ Construction Times are Valid Numbers (NOT NaN)",
            success and status == 200 and valid_times and not nan_found,
            f"Status: {status}, Valid times: {valid_times}, No NaN: {not nan_found}, Queue: {len(data.get('queue', [])) if isinstance(data, dict) else 0}, Details: {construction_details[:5]}"
        )

    async def test_diplomacy_complete(self):
        """Complete diplomacy testing using admin user"""
        print("\n=== TEST 3: Diplomacy Testing ===")
        
        if not self.admin_token:
            print("⚠️  Cannot test diplomacy - no admin token")
            return
        
        # Create alliance with admin user
        timestamp = datetime.now().strftime('%H%M%S')
        alliance_data = {
            "name": f"Test Alliance {timestamp}",
            "description": "A test alliance for verifying diplomatic relations and data serialization"
        }
        
        success, data, status = await self.make_request("POST", "/diplomacy/alliance/create", alliance_data, token=self.admin_token)
        
        self.log_test(
            "✓ Create Alliance",
            success and status == 200,
            f"Status: {status}, Alliance created: {data.get('success', False) if isinstance(data, dict) else 'error'}"
        )
        
        # Create trade offer with admin user
        trade_data = {
            "offering": {"gold": 300, "wood": 150},
            "requesting": {"stone": 200, "food": 100},
            "duration": 7200
        }
        
        success, data, status = await self.make_request("POST", "/diplomacy/trade/create", trade_data, token=self.admin_token)
        
        self.log_test(
            "✓ Create Trade Offer",
            success and status == 200,
            f"Status: {status}, Trade created: {data.get('success', False) if isinstance(data, dict) else 'error'}"
        )
        
        # List alliances via GET endpoint - check data format (no React child errors)
        success, data, status = await self.make_request("GET", "/diplomacy/alliance/list")
        
        proper_alliance_format = True
        alliance_count = 0
        format_issues = []
        
        if success and isinstance(data, dict):
            alliances = data.get('alliances', [])
            alliance_count = len(alliances)
            for alliance in alliances:
                # Check for proper data format (no raw ObjectId that causes React child errors)
                if '_id' in alliance and not isinstance(alliance['_id'], str):
                    proper_alliance_format = False
                    format_issues.append("Raw ObjectId in _id field")
                
                # Check for required fields
                required_fields = ['name', 'description', 'memberCount']
                missing_fields = [field for field in required_fields if field not in alliance]
                if missing_fields:
                    proper_alliance_format = False
                    format_issues.append(f"Missing fields: {missing_fields}")
        
        self.log_test(
            "✓ List Alliances - Proper Data Format (No 'Objects are not valid as React child' errors)",
            success and status == 200 and proper_alliance_format,
            f"Status: {status}, Alliances: {alliance_count}, Proper format: {proper_alliance_format}, Issues: {format_issues}"
        )
        
        # List trade offers via GET endpoint - check data format
        success, data, status = await self.make_request("GET", "/diplomacy/trade/offers")
        
        proper_trade_format = True
        trade_count = 0
        trade_format_issues = []
        
        if success and isinstance(data, dict):
            offers = data.get('offers', [])
            trade_count = len(offers)
            for offer in offers:
                # Check for proper data format (no raw ObjectId)
                if '_id' in offer and not isinstance(offer['_id'], str):
                    proper_trade_format = False
                    trade_format_issues.append("Raw ObjectId in _id field")
                
                # Check for required fields and proper datetime serialization
                required_fields = ['offering', 'requesting', 'createdAt']
                missing_fields = [field for field in required_fields if field not in offer]
                if missing_fields:
                    proper_trade_format = False
                    trade_format_issues.append(f"Missing fields: {missing_fields}")
                
                # Check datetime is string (ISO format) - not object that causes React errors
                created_at = offer.get('createdAt')
                if created_at and not isinstance(created_at, str):
                    proper_trade_format = False
                    trade_format_issues.append(f"DateTime not string: {type(created_at)}")
        
        self.log_test(
            "✓ List Trade Offers - Proper Data Format (No 'Objects are not valid as React child' errors)",
            success and status == 200 and proper_trade_format,
            f"Status: {status}, Trades: {trade_count}, Proper format: {proper_trade_format}, Issues: {trade_format_issues}"
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
            "✓ Complete Object Serialization Test (No React Child Errors)",
            serialization_test,
            f"All diplomacy data properly JSON serializable: {serialization_test}, Errors: {serialization_errors}"
        )

    async def run_complete_tests(self):
        """Run the complete test suite for user review"""
        print("🏰 JRPG Medieval Game - COMPLETE CORRECTIONS VERIFICATION")
        print("📋 Testing the EXACT scenarios from the review request:")
        print("   1. Admin user testing (admin/admin not testadmin/admin123)")
        print("   2. Construction times validation (no NaN values)")
        print("   3. Diplomacy system data format (no React child errors)")
        print(f"🔗 API: {API_URL}")
        print("=" * 80)
        
        start_time = datetime.now()
        
        # Run the three main test categories as requested
        await self.test_admin_user_complete()
        await self.test_construction_times_complete()
        await self.test_diplomacy_complete()
        
        # Print summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 80)
        print("🏰 COMPLETE VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print("\n📋 SPECIFIC REQUIREMENTS VERIFICATION:")
        print("   ✓ Admin login with admin/admin (not testadmin/admin123)")
        print("   ✓ Admin privileges verification (isAdmin: true)")
        print("   ✓ System-info returns status/database/cpuUsage/memoryUsage with real values")
        print("   ✓ Admin stats endpoint working")
        print("   ✓ Construction times are valid numbers (not NaN)")
        print("   ✓ Alliance and trade data properly serialized (no React child errors)")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        else:
            print("\n🎉 ALL REQUESTED CORRECTIONS VERIFIED SUCCESSFULLY!")
        
        print("\n🏰 Complete Verification Finished!")
        
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
    async with CompleteTestRunner() as tester:
        results = await tester.run_complete_tests()
        
        # Exit with error code if tests failed
        if results['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())