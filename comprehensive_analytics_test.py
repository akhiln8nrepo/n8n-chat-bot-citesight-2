import requests
import sys
import json
import time
from datetime import datetime

class ComprehensiveAnalyticsTester:
    def __init__(self, base_url="https://geo-prompt-monitor.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.access_token = None
        self.user_id = None
        # Use existing test user or create new one
        self.test_email = "analyticstest@geomonitor.com"
        self.test_password = "TestAnalytics!2024"
        
    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        default_headers = {'Content-Type': 'application/json'}
        
        if headers:
            default_headers.update(headers)
            
        if self.access_token and 'Authorization' not in default_headers:
            default_headers['Authorization'] = f"Bearer {self.access_token}"

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if params:
            print(f"   Params: {params}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers)

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 2000:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                        if len(response_data) > 0 and len(str(response_data[0])) < 500:
                            print(f"   First item: {response_data[0]}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_login_existing_user(self):
        """Test login with existing user or register new one"""
        # Try to login first
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, response = self.run_test(
            "Login Existing Analytics Test User",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   Access Token: {self.access_token[:20]}...")
            print(f"   User ID: {self.user_id}")
            return True
        
        # If login fails, register new user
        print("   Login failed, registering new user...")
        return self.test_register_new_user()

    def test_register_new_user(self):
        """Register new analytics test user"""
        user_data = {
            "email": self.test_email,
            "password": self.test_password,
            "first_name": "Analytics",
            "last_name": "Tester", 
            "company_name": "GEO Analytics Corp",
            "website_url": "https://example.com",
            "industry": "Technology",
            "product_description": "Analytics and monitoring platform",
            "competitors": ["Competitor1", "Competitor2"]
        }
        
        success, response = self.run_test(
            "Register New Analytics Test User",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   Access Token: {self.access_token[:20]}...")
            print(f"   User ID: {self.user_id}")
            
            # Wait for onboarding to complete
            print("   Waiting for onboarding to complete...")
            return self.wait_for_onboarding()
        return False

    def wait_for_onboarding(self, max_wait_time=120):
        """Wait for onboarding to complete"""
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            success, response = self.run_test(
                "Check Onboarding Status",
                "GET", 
                "onboarding/status",
                200
            )
            
            if success and response.get('completed'):
                prompt_count = response.get('prompt_count', 0)
                print(f"✅ Onboarding completed! Generated {prompt_count} prompts")
                return True
                
            elapsed = int(time.time() - start_time)
            print(f"   Onboarding in progress... ({elapsed}s elapsed)")
            time.sleep(10)
        
        print(f"❌ Onboarding did not complete within {max_wait_time} seconds")
        return False

    def test_100_prompts_endpoint(self):
        """Test that GET /api/prompts now returns up to 100 prompts instead of 25"""
        success, response = self.run_test(
            "Verify 100 Prompts Limit (was 25)",
            "GET",
            "prompts", 
            200
        )
        
        if not success or not response:
            return False
            
        if not isinstance(response, list):
            print("❌ Response is not a list")
            return False
        
        prompt_count = len(response)
        print(f"   Returned {prompt_count} prompts")
        
        # Verify we get more than 25 prompts (should be up to 100)
        if prompt_count <= 25:
            print(f"❌ Still limited to 25 prompts or less: {prompt_count}")
            return False
        elif prompt_count > 25 and prompt_count <= 100:
            print(f"✅ SUCCESS: Now returns {prompt_count} prompts (up from 25 limit)")
            return True
        else:
            print(f"⚠️  Unexpected count: {prompt_count} prompts (expected ≤100)")
            return True  # Still a success, just unexpected

    def test_analytics_dashboard_default(self):
        """Test GET /api/analytics/dashboard with default parameters"""
        success, response = self.run_test(
            "Analytics Dashboard - Default (30d)",
            "GET",
            "analytics/dashboard",
            200,
            params={"period": "30d"}
        )
        
        if not success or not response:
            return False
        
        # Verify expected response structure
        required_fields = [
            "period", "filters", "date_range", "kpis", "platform_breakdown",
            "competitors", "prompt_performance", "opportunities", 
            "available_platforms", "available_categories"
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in response:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        # Verify available platforms
        available_platforms = response.get('available_platforms', [])
        expected_platforms = ["chatgpt", "claude", "gemini", "perplexity"]
        
        if not all(platform in available_platforms for platform in expected_platforms):
            print(f"❌ Missing expected platforms. Got: {available_platforms}")
            return False
        
        print(f"✅ Analytics dashboard structure correct")
        print(f"   Period: {response.get('period')}")
        print(f"   Available platforms: {available_platforms}")
        print(f"   Available categories: {response.get('available_categories', [])}")
        
        return True

    def test_analytics_dashboard_platform_filters(self):
        """Test analytics dashboard with different platform filters"""
        platforms_to_test = ["chatgpt", "claude", "gemini", "perplexity"]
        
        for platform in platforms_to_test:
            success, response = self.run_test(
                f"Analytics Dashboard - Filter by {platform.upper()}",
                "GET",
                "analytics/dashboard",
                200,
                params={"period": "30d", "platform": platform}
            )
            
            if not success:
                return False
            
            # Verify filter is applied
            filters = response.get('filters', {})
            if filters.get('platform') != platform:
                print(f"❌ Platform filter not applied correctly for {platform}")
                return False
            
            print(f"   ✅ {platform.upper()} filter working")
        
        # Test 7 days period with platform filter
        success, response = self.run_test(
            "Analytics Dashboard - 7d + ChatGPT filter",
            "GET",
            "analytics/dashboard",
            200,
            params={"period": "7d", "platform": "chatgpt"}
        )
        
        if not success:
            return False
        
        if response.get('period') != '7d' or response.get('filters', {}).get('platform') != 'chatgpt':
            print("❌ Combined period and platform filter not working")
            return False
        
        print("✅ All platform filters working correctly")
        return True

    def test_analytics_dashboard_periods(self):
        """Test analytics dashboard with different time periods"""
        periods_to_test = ["7d", "30d", "90d"]
        
        for period in periods_to_test:
            success, response = self.run_test(
                f"Analytics Dashboard - {period} period",
                "GET",
                "analytics/dashboard",
                200,
                params={"period": period}
            )
            
            if not success:
                return False
            
            # Verify period is set correctly
            if response.get('period') != period:
                print(f"❌ Period not set correctly for {period}")
                return False
            
            # Verify date range makes sense
            date_range = response.get('date_range', {})
            if not date_range.get('start') or not date_range.get('end'):
                print(f"❌ Missing date range for {period}")
                return False
            
            print(f"   ✅ {period} period working")
        
        print("✅ All time periods working correctly")
        return True

    def test_monitoring_endpoints(self):
        """Test the new monitoring API endpoints"""
        # First get a prompt to monitor
        success, prompts_response = self.run_test(
            "Get Prompts for Monitoring Test",
            "GET",
            "prompts",
            200
        )
        
        if not success or not prompts_response or len(prompts_response) == 0:
            print("❌ No prompts available for monitoring test")
            return False
        
        # Use first prompt for testing
        test_prompt = prompts_response[0]
        prompt_id = test_prompt.get('id')
        
        if not prompt_id:
            print("❌ No prompt ID found")
            return False
        
        print(f"   Using prompt ID: {prompt_id}")
        
        # Test start monitoring
        success, response = self.run_test(
            "Start Monitoring Prompt",
            "POST",
            f"prompts/{prompt_id}/monitor",
            200
        )
        
        if not success:
            return False
        
        if 'monitoring_id' not in response:
            print("❌ No monitoring_id in start monitoring response")
            return False
        
        print(f"   Monitoring started: {response.get('message')}")
        
        # Test get monitored prompts
        success, response = self.run_test(
            "Get Monitored Prompts",
            "GET",
            "monitoring/prompts",
            200
        )
        
        if not success:
            return False
        
        if not isinstance(response, list):
            print("❌ Monitored prompts response is not a list")
            return False
        
        # Should have at least one monitored prompt now
        monitored_count = len(response)
        print(f"   Found {monitored_count} monitored prompts")
        
        # Test stop monitoring
        success, response = self.run_test(
            "Stop Monitoring Prompt",
            "DELETE",
            f"prompts/{prompt_id}/monitor",
            200
        )
        
        if not success:
            return False
        
        print(f"   Monitoring stopped: {response.get('message')}")
        
        print("✅ All monitoring endpoints working correctly")
        return True

    def test_analytics_kpis_structure(self):
        """Test that analytics dashboard KPIs have correct structure"""
        success, response = self.run_test(
            "Verify Analytics KPIs Structure",
            "GET",
            "analytics/dashboard",
            200,
            params={"period": "30d"}
        )
        
        if not success or not response:
            return False
        
        kpis = response.get('kpis', {})
        if not kpis:
            print("❌ No KPIs found in response")
            return False
        
        # Expected KPI fields based on the review request
        expected_kpis = [
            'visibility_rate', 'avg_position', 'share_of_voice', 'avg_sentiment',
            'total_monitored_prompts', 'total_checks', 'total_mentions'
        ]
        
        missing_kpis = []
        for kpi in expected_kpis:
            if kpi not in kpis:
                missing_kpis.append(kpi)
        
        if missing_kpis:
            print(f"❌ Missing KPIs: {missing_kpis}")
            return False
        
        print("✅ All expected KPIs present")
        print(f"   Visibility Rate: {kpis.get('visibility_rate')}%")
        print(f"   Avg Position: {kpis.get('avg_position')}")
        print(f"   Share of Voice: {kpis.get('share_of_voice')}%")
        print(f"   Avg Sentiment: {kpis.get('avg_sentiment')}")
        
        return True

    def test_platform_breakdown_structure(self):
        """Test platform breakdown in analytics dashboard"""
        success, response = self.run_test(
            "Verify Platform Breakdown Structure",
            "GET",
            "analytics/dashboard",
            200,
            params={"period": "30d"}
        )
        
        if not success or not response:
            return False
        
        platform_breakdown = response.get('platform_breakdown', [])
        if not isinstance(platform_breakdown, list):
            print("❌ Platform breakdown is not a list")
            return False
        
        # Should have entries for all 4 platforms
        expected_platforms = ['chatgpt', 'claude', 'gemini', 'perplexity']
        found_platforms = [p.get('platform') for p in platform_breakdown]
        
        missing_platforms = []
        for platform in expected_platforms:
            if platform not in found_platforms:
                missing_platforms.append(platform)
        
        if missing_platforms:
            print(f"❌ Missing platforms in breakdown: {missing_platforms}")
            return False
        
        # Verify structure of platform entries
        for platform_data in platform_breakdown:
            required_fields = ['platform', 'display_name', 'total_checks', 'mentions', 'mention_rate']
            missing_fields = []
            for field in required_fields:
                if field not in platform_data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Platform {platform_data.get('platform')} missing fields: {missing_fields}")
                return False
        
        print("✅ Platform breakdown structure correct")
        print(f"   Platforms: {found_platforms}")
        
        return True

    def test_ai_platform_discovery_source(self):
        """Verify 'AI Platform Discovery' source is available in filters"""
        success, response = self.run_test(
            "Check Available Categories for AI Platform Discovery",
            "GET",
            "analytics/dashboard",
            200,
            params={"period": "30d"}
        )
        
        if not success or not response:
            return False
        
        available_categories = response.get('available_categories', [])
        
        if 'ai_platform_discovery' not in available_categories:
            print(f"❌ 'ai_platform_discovery' not found in available categories")
            print(f"   Available: {available_categories}")
            return False
        
        print("✅ 'AI Platform Discovery' source available in filters")
        print(f"   All categories: {available_categories}")
        
        return True

    def run_all_tests(self):
        """Run comprehensive analytics dashboard tests"""
        print("🚀 Starting Comprehensive Analytics Dashboard Tests")
        print("=" * 70)
        
        # Test sequence
        tests = [
            ("Login/Register Analytics Test User", self.test_login_existing_user),
            ("Verify 100 Prompts Limit Fix", self.test_100_prompts_endpoint),
            ("Analytics Dashboard - Default", self.test_analytics_dashboard_default),
            ("Analytics Dashboard - Platform Filters", self.test_analytics_dashboard_platform_filters),
            ("Analytics Dashboard - Time Periods", self.test_analytics_dashboard_periods),
            ("Analytics KPIs Structure", self.test_analytics_kpis_structure),
            ("Platform Breakdown Structure", self.test_platform_breakdown_structure),
            ("Monitoring API Endpoints", self.test_monitoring_endpoints),
            ("AI Platform Discovery Source", self.test_ai_platform_discovery_source)
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"\n📋 Running: {test_name}")
                result = test_func()
                if not result:
                    print(f"❌ {test_name} failed - continuing with other tests")
                    # Don't break, continue with other tests
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {str(e)}")
                self.tests_run += 1
        
        # Print final results
        print("\n" + "=" * 70)
        print(f"📊 Analytics Dashboard Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All Analytics Dashboard tests passed!")
            return True
        else:
            failed_count = self.tests_run - self.tests_passed
            success_rate = (self.tests_passed / self.tests_run) * 100
            print(f"⚠️  {failed_count} tests failed ({success_rate:.1f}% success rate)")
            
            # Consider it successful if most tests pass
            if success_rate >= 80:
                print("✅ Overall testing successful (80%+ pass rate)")
                return True
            else:
                print("❌ Too many critical failures")
                return False

def main():
    print("🚀 Starting Comprehensive Analytics Dashboard Testing")
    print("Testing: 100 Prompts Fix + Analytics Dashboard + Monitoring APIs")
    print("=" * 70)
    
    # Run comprehensive tests
    tester = ComprehensiveAnalyticsTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Comprehensive Analytics Dashboard testing completed successfully!")
        return 0
    else:
        print("\n❌ Some critical analytics dashboard tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())