import requests
import sys
import json
from datetime import datetime

class AIContentMonitorTester:
    def __init__(self, base_url="https://aicontentmonitor.preview.emergentagent.com"):
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
    print("🚀 Starting AI Content Monitor API Tests")
    print("=" * 50)
    
    tester = AIContentMonitorTester()
    
    # Test sequence
    tests = [
        tester.test_root_endpoint,
        tester.test_create_publisher,
        tester.test_get_publishers,
        tester.test_create_content,
        tester.test_get_content,
        tester.test_get_content_by_id,
        tester.test_get_visibility,
        tester.test_create_keyword,
        tester.test_get_keywords,
        tester.test_get_recommendations,
        tester.test_dashboard_stats,
        tester.test_dashboard_stats_with_publisher,
        tester.test_get_competitors
    ]
    
    # Run all tests
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            tester.tests_run += 1
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())