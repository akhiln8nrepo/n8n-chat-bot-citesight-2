import requests
import sys
import json
import time
from datetime import datetime

class GEOPromptFrameworkTester:
    def __init__(self, base_url="https://promptr-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.access_token = None
        self.user_id = None
        self.test_email = f"testadidas@geomonitor.com"
        
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
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers)

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 1000:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                        if len(response_data) > 0:
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

    def test_register_adidas_user(self):
        """Test user registration with Adidas sportswear company data"""
        user_data = {
            "email": self.test_email,
            "password": "Test123!",
            "first_name": "Test",
            "last_name": "Adidas", 
            "company_name": "Adidas",
            "website_url": "https://www.adidas.com",
            "industry": "Sportswear & Athletic Apparel",
            "product_description": "Premium athletic footwear and sportswear brand specializing in running shoes, football boots, and lifestyle sneakers",
            "competitors": ["Nike", "Puma", "Under Armour"]
        }
        
        success, response = self.run_test(
            "Register Adidas User for GEO Framework Testing",
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
            return True
        return False

    def test_onboarding_status(self, max_wait_time=120):
        """Wait for onboarding to complete"""
        print(f"\n🔍 Waiting for onboarding to complete (max {max_wait_time}s)...")
        
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
                
            print(f"   Onboarding in progress... ({int(time.time() - start_time)}s elapsed)")
            time.sleep(5)
        
        print(f"❌ Onboarding did not complete within {max_wait_time} seconds")
        return False

    def test_sportswear_prompts_relevance(self):
        """Verify prompts are relevant to sportswear/athletic apparel industry"""
        success, response = self.run_test(
            "Get Sportswear-Relevant Prompts",
            "GET",
            "prompts", 
            200
        )
        
        if not success or not response:
            return False
            
        if not isinstance(response, list) or len(response) == 0:
            print("❌ No prompts found")
            return False
        
        print(f"✅ Generated {len(response)} prompts")
        
        # Check for sportswear-relevant prompts
        sportswear_keywords = [
            'running shoes', 'athletic', 'sportswear', 'sneakers', 'football boots',
            'adidas', 'nike', 'puma', 'under armour', 'shoes', 'footwear', 'apparel'
        ]
        
        relevant_prompts = []
        for prompt in response:
            prompt_text = prompt.get('prompt', '').lower()
            if any(keyword in prompt_text for keyword in sportswear_keywords):
                relevant_prompts.append(prompt)
        
        relevance_percentage = (len(relevant_prompts) / len(response)) * 100
        print(f"   Sportswear relevance: {relevance_percentage:.1f}% ({len(relevant_prompts)}/{len(response)} prompts)")
        
        # Show sample relevant prompts
        print("   Sample relevant prompts:")
        for i, prompt in enumerate(relevant_prompts[:5]):
            print(f"     {i+1}. {prompt.get('prompt')}")
        
        if relevance_percentage < 40:
            print(f"❌ Low relevance: Only {relevance_percentage:.1f}% of prompts are sportswear-related")
            return False
        
        print(f"✅ Good relevance: {relevance_percentage:.1f}% of prompts are sportswear-related")
        return True

    def test_stats_endpoint_7_metrics(self):
        """Verify stats endpoint returns all 7 metrics including intent breakdown"""
        success, response = self.run_test(
            "Get Stats with 7 Metrics",
            "GET",
            "prompts/stats",
            200
        )
        
        if not success or not response:
            return False
            
        required_stats = [
            'avg_business_value', 'avg_volume', 'avg_competition', 'avg_feasibility',
            'avg_intent_score', 'avg_citation_potential', 'avg_brand_relevance',
            'intent_breakdown'
        ]
        
        missing_stats = []
        for stat in required_stats:
            if stat not in response:
                missing_stats.append(stat)
                
        if missing_stats:
            print(f"❌ Missing stats: {missing_stats}")
            return False
            
        print(f"✅ All 7 metric stats present including intent_breakdown")
        print(f"   avg_intent_score: {response.get('avg_intent_score')}")
        print(f"   intent_breakdown: {response.get('intent_breakdown')}")
        
        return True

    def run_all_tests(self):
        """Run complete 7-factor scoring test flow"""
        print("🚀 Starting 7-Factor Scoring Algorithm Tests")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Register User", self.test_register_user),
            ("Wait for Onboarding", self.test_onboarding_status), 
            ("Verify 7 Metrics in Prompts", self.test_prompts_have_7_metrics),
            ("Verify 7 Metrics in Stats", self.test_stats_endpoint_7_metrics)
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"\n📋 Running: {test_name}")
                result = test_func()
                if not result:
                    print(f"❌ {test_name} failed - stopping test sequence")
                    break
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {str(e)}")
                self.tests_run += 1
                break
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 7-Factor Scoring Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All 7-factor scoring tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False


class AIContentMonitorTester:
    def __init__(self, base_url="https://promptr-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.publisher_id = None
        self.content_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
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

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_create_publisher(self):
        """Test creating a publisher"""
        publisher_data = {
            "name": f"Test Publisher {datetime.now().strftime('%H%M%S')}",
            "email": "test@publisher.com",
            "website": "https://testpublisher.com"
        }
        
        success, response = self.run_test(
            "Create Publisher",
            "POST",
            "publishers",
            200,
            data=publisher_data
        )
        
        if success and 'id' in response:
            self.publisher_id = response['id']
            print(f"   Publisher ID: {self.publisher_id}")
            return True
        return False

    def test_get_publishers(self):
        """Test getting all publishers"""
        return self.run_test("Get Publishers", "GET", "publishers", 200)

    def test_create_content(self):
        """Test creating content"""
        if not self.publisher_id:
            print("❌ Cannot test content creation - no publisher ID")
            return False
            
        content_data = {
            "publisher_id": self.publisher_id,
            "title": "AI Content Marketing Best Practices",
            "url": "https://example.com/ai-content-marketing",
            "content_text": "Artificial intelligence is revolutionizing content marketing by enabling personalized experiences, automated content generation, and predictive analytics. This comprehensive guide explores how AI tools can enhance your content strategy, improve audience engagement, and drive better ROI. From natural language processing to machine learning algorithms, discover the key technologies shaping the future of digital marketing."
        }
        
        success, response = self.run_test(
            "Create Content",
            "POST",
            "content",
            200,
            data=content_data
        )
        
        if success and 'id' in response:
            self.content_id = response['id']
            print(f"   Content ID: {self.content_id}")
            return True
        return False

    def test_get_content(self):
        """Test getting all content"""
        return self.run_test("Get All Content", "GET", "content", 200)

    def test_get_content_by_id(self):
        """Test getting specific content by ID"""
        if not self.content_id:
            print("❌ Cannot test get content by ID - no content ID")
            return False
            
        return self.run_test(
            "Get Content by ID",
            "GET",
            f"content/{self.content_id}",
            200
        )

    def test_get_visibility(self):
        """Test getting visibility data for content"""
        if not self.content_id:
            print("❌ Cannot test visibility - no content ID")
            return False
            
        return self.run_test(
            "Get Visibility Data",
            "GET",
            f"visibility/{self.content_id}",
            200
        )

    def test_create_keyword(self):
        """Test creating a keyword"""
        if not self.content_id:
            print("❌ Cannot test keyword creation - no content ID")
            return False
            
        keyword_data = {
            "content_id": self.content_id,
            "keyword": "AI content marketing"
        }
        
        return self.run_test(
            "Create Keyword",
            "POST",
            "keywords",
            200,
            data=keyword_data
        )

    def test_get_keywords(self):
        """Test getting keywords for content"""
        if not self.content_id:
            print("❌ Cannot test get keywords - no content ID")
            return False
            
        return self.run_test(
            "Get Keywords",
            "GET",
            f"keywords/{self.content_id}",
            200
        )

    def test_get_recommendations(self):
        """Test getting recommendations for content"""
        if not self.content_id:
            print("❌ Cannot test get recommendations - no content ID")
            return False
            
        return self.run_test(
            "Get Recommendations",
            "GET",
            f"recommendations/{self.content_id}",
            200
        )

    def test_dashboard_stats(self):
        """Test getting dashboard statistics"""
        return self.run_test("Get Dashboard Stats", "GET", "dashboard/stats", 200)

    def test_dashboard_stats_with_publisher(self):
        """Test getting dashboard statistics for specific publisher"""
        if not self.publisher_id:
            print("❌ Cannot test publisher-specific stats - no publisher ID")
            return False
            
        return self.run_test(
            "Get Dashboard Stats (Publisher)",
            "GET",
            "dashboard/stats",
            200,
            params={"publisher_id": self.publisher_id}
        )

    def test_get_competitors(self):
        """Test getting competitor analysis"""
        if not self.publisher_id:
            print("❌ Cannot test competitors - no publisher ID")
            return False
            
        return self.run_test(
            "Get Competitors",
            "GET",
            "competitors",
            200,
            params={"publisher_id": self.publisher_id}
        )

def main():
    print("🚀 Starting CiteSight API Tests")
    print("=" * 50)
    
    # Run 7-Factor Scoring Tests
    seven_factor_tester = SevenFactorScoringTester()
    seven_factor_success = seven_factor_tester.run_all_tests()
    
    if not seven_factor_success:
        print("\n❌ 7-Factor Scoring tests failed")
        return 1
    
    print("\n" + "=" * 50)
    print("🎉 All CiteSight tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())