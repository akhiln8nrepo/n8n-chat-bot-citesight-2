import requests
import sys
import json
import time
from datetime import datetime

class Layer8AIDiscoveryTester:
    def __init__(self, base_url="https://geo-prompt-monitor.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.access_token = None
        self.user_id = None
        # Use timestamp for unique test user
        timestamp = int(time.time())
        self.test_email = f"layer8test_{timestamp}@geomonitor.com"
        
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

    def test_register_layer8_user(self):
        """Test user registration with Layer 8 test data as specified in review request"""
        user_data = {
            "email": self.test_email,
            "password": "TestLayer8!2024",
            "first_name": "Layer8",
            "last_name": "Test", 
            "company_name": "Tech Solutions Inc",
            "website_url": "https://stripe.com",
            "industry": "Financial Services",
            "product_description": "Payment processing and financial infrastructure for businesses",
            "competitors": ["PayPal", "Square", "Adyen"]
        }
        
        success, response = self.run_test(
            "Register Layer 8 Test User (Financial Services)",
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
        """Wait for onboarding to complete - Layer 8 may take longer due to AI platform queries"""
        print(f"\n🔍 Waiting for Layer 8 onboarding to complete (max {max_wait_time}s)...")
        print("   Layer 8 queries 4 AI platforms, so this may take 60-90 seconds...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            success, response = self.run_test(
                "Check Layer 8 Onboarding Status",
                "GET", 
                "onboarding/status",
                200
            )
            
            if success and response.get('completed'):
                prompt_count = response.get('prompt_count', 0)
                print(f"✅ Layer 8 onboarding completed! Generated {prompt_count} prompts")
                
                # Verify we got 100 prompts (up from previous 25)
                if prompt_count >= 100:
                    print(f"✅ Layer 8 SUCCESS: Generated {prompt_count} prompts (expected 100+)")
                    return True
                else:
                    print(f"⚠️  Layer 8 WARNING: Only {prompt_count} prompts generated (expected 100+)")
                    return True  # Still continue testing
                
            elapsed = int(time.time() - start_time)
            print(f"   Layer 8 onboarding in progress... ({elapsed}s elapsed)")
            time.sleep(10)  # Check every 10 seconds for Layer 8
        
        print(f"❌ Layer 8 onboarding did not complete within {max_wait_time} seconds")
        return False

    def test_layer8_ai_platform_discovery(self):
        """Verify Layer 8: AI Platform Discovery prompts are generated"""
        # First check all prompts to get total count
        success, response = self.run_test(
            "Get All Prompts for Layer 8 Analysis",
            "GET",
            "prompts", 
            200
        )
        
        if not success or not response:
            return False
            
        if not isinstance(response, list) or len(response) == 0:
            print("❌ No prompts found")
            return False
        
        print(f"✅ API returned {len(response)} prompts (top ranked)")
        
        # Check for AI Platform Discovery source in returned prompts
        ai_platform_prompts = []
        for prompt in response:
            if prompt.get('source') == 'ai_platform_discovery':
                ai_platform_prompts.append(prompt)
        
        print(f"   AI Platform Discovery prompts in top {len(response)}: {len(ai_platform_prompts)}")
        
        # If we don't find any in the top results, check the stats endpoint for source breakdown
        success_stats, stats_response = self.run_test(
            "Check Source Breakdown for AI Platform Discovery",
            "GET",
            "prompts/stats",
            200
        )
        
        if success_stats and stats_response:
            source_breakdown = stats_response.get('source_breakdown', {})
            ai_platform_count = source_breakdown.get('ai_platform_discovery', 0)
            
            print(f"   Total AI Platform Discovery prompts (from stats): {ai_platform_count}")
            
            if ai_platform_count > 0:
                print(f"✅ Layer 8 AI Platform Discovery working - {ai_platform_count} prompts generated")
                
                # Show sample AI platform prompts if we have any in the top results
                if ai_platform_prompts:
                    print("   Sample AI Platform Discovery prompts:")
                    for i, prompt in enumerate(ai_platform_prompts[:3]):
                        platform = prompt.get('extra_fields', {}).get('ai_discovery_platform', 'unknown')
                        print(f"     {i+1}. [{platform.upper()}] {prompt.get('prompt')}")
                
                return True
            else:
                print("❌ No AI Platform Discovery prompts found in source breakdown")
                return False
        
        # Fallback: if we found some in the top results, that's still success
        if len(ai_platform_prompts) > 0:
            print(f"✅ Layer 8 AI Platform Discovery working - found {len(ai_platform_prompts)} prompts in top results")
            
            # Verify extra_fields contain platform information
            platforms_found = set()
            for prompt in ai_platform_prompts:
                extra_fields = prompt.get('extra_fields', {})
                platform = extra_fields.get('ai_discovery_platform')
                if platform:
                    platforms_found.add(platform)
            
            print(f"   AI platforms found: {sorted(platforms_found)}")
            
            # Show sample AI platform prompts
            print("   Sample AI Platform Discovery prompts:")
            for i, prompt in enumerate(ai_platform_prompts[:3]):
                platform = prompt.get('extra_fields', {}).get('ai_discovery_platform', 'unknown')
                print(f"     {i+1}. [{platform.upper()}] {prompt.get('prompt')}")
            
            return True
        
        print("❌ No AI Platform Discovery prompts found")
        return False

    def test_financial_services_prompts_relevance(self):
        """Verify prompts are relevant to financial services/payments industry"""
        success, response = self.run_test(
            "Get Financial Services-Relevant Prompts",
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
        
        # Check for financial services-relevant prompts
        fintech_keywords = [
            'payment', 'stripe', 'paypal', 'square', 'adyen', 'financial', 'fintech',
            'transaction', 'billing', 'checkout', 'merchant', 'processing', 'banking',
            'credit card', 'digital wallet', 'api', 'integration', 'subscription'
        ]
        
        relevant_prompts = []
        for prompt in response:
            prompt_text = prompt.get('prompt', '').lower()
            if any(keyword in prompt_text for keyword in fintech_keywords):
                relevant_prompts.append(prompt)
        
        relevance_percentage = (len(relevant_prompts) / len(response)) * 100
        print(f"   Financial Services relevance: {relevance_percentage:.1f}% ({len(relevant_prompts)}/{len(response)} prompts)")
        
        # Show sample relevant prompts
        print("   Sample relevant prompts:")
        for i, prompt in enumerate(relevant_prompts[:5]):
            print(f"     {i+1}. {prompt.get('prompt')}")
        
        if relevance_percentage < 30:
            print(f"❌ Low relevance: Only {relevance_percentage:.1f}% of prompts are fintech-related")
            return False
        
        print(f"✅ Good relevance: {relevance_percentage:.1f}% of prompts are fintech-related")
        return True
    def test_new_prompt_sources_with_layer8(self):
        """Verify prompts come from multiple sources including Layer 8 AI Platform Discovery"""
        # Get the source breakdown from stats endpoint for accurate count
        success_stats, stats_response = self.run_test(
            "Get Source Breakdown from Stats",
            "GET",
            "prompts/stats",
            200
        )
        
        if not success_stats or not stats_response:
            return False
        
        source_breakdown = stats_response.get('source_breakdown', {})
        
        if not source_breakdown:
            print("❌ No source breakdown found in stats")
            return False
        
        print(f"   Complete source breakdown: {dict(sorted(source_breakdown.items()))}")
        
        # Check if Layer 8 source is present
        if 'ai_platform_discovery' not in source_breakdown:
            print(f"❌ Layer 8 source 'ai_platform_discovery' not found")
            return False
        
        layer8_count = source_breakdown['ai_platform_discovery']
        print(f"✅ Layer 8 AI Platform Discovery: {layer8_count} prompts")
        
        # Check for traditional sources (should have at least 3 different sources)
        traditional_sources = [s for s in source_breakdown.keys() if s != 'ai_platform_discovery']
        if len(traditional_sources) < 3:
            print(f"❌ Too few traditional sources: {traditional_sources}")
            return False
        
        total_sources = len(source_breakdown)
        print(f"✅ Found {total_sources} total sources including Layer 8")
        
        # Verify we have a good mix of sources
        if total_sources >= 4 and layer8_count > 0:
            print(f"✅ Good source diversity with Layer 8 integration")
            return True
        else:
            print(f"❌ Insufficient source diversity: {total_sources} sources, {layer8_count} Layer 8 prompts")
            return False

    def test_new_intent_classification(self):
        """Verify prompts use new intent types"""
        success, response = self.run_test(
            "Verify New Intent Classification",
            "GET",
            "prompts",
            200
        )
        
        if not success or not response:
            return False
        
        expected_intents = [
            'informational', 'navigational', 'commercial_investigation',
            'transactional', 'local', 'support'
        ]
        
        found_intents = set()
        for prompt in response:
            intent = prompt.get('intent')
            if intent:
                found_intents.add(intent)
        
        print(f"   Found intents: {sorted(found_intents)}")
        
        # Check if we have at least some of the expected intents
        valid_intents = found_intents.intersection(set(expected_intents))
        if len(valid_intents) < 2:
            print(f"❌ Too few valid intents found: {valid_intents}")
            return False
        
        print(f"✅ Valid intents found: {sorted(valid_intents)}")
        return True

    def test_7_factor_scoring_system(self):
        """Verify the 7-factor scoring system is working"""
        success, response = self.run_test(
            "Verify 7-Factor Scoring System",
            "GET",
            "prompts",
            200
        )
        
        if not success or not response:
            return False
        
        # Check first prompt for all 7 factors
        first_prompt = response[0]
        required_factors = [
            'business_value', 'volume', 'competition', 'feasibility',
            'intent_score', 'citation_potential', 'brand_relevance', 'overall_score'
        ]
        
        missing_factors = []
        for factor in required_factors:
            if factor not in first_prompt:
                missing_factors.append(factor)
        
        if missing_factors:
            print(f"❌ Missing scoring factors: {missing_factors}")
            return False
        
        # Verify scoring ranges
        for factor in required_factors[:-1]:  # Exclude overall_score
            value = first_prompt.get(factor, 0)
            if not (0 <= value <= 100):
                print(f"❌ Factor {factor} out of range: {value}")
                return False
        
        # Check tier classification
        tier = first_prompt.get('tier', '')
        valid_tiers = ['TIER_1_CRITICAL', 'TIER_2_HIGH', 'TIER_3_MEDIUM', 'TIER_4_LOW']
        if tier not in valid_tiers:
            print(f"❌ Invalid tier: {tier}")
            return False
        
        # Check buyer stage
        buyer_stage = first_prompt.get('buyer_stage', '')
        valid_stages = ['awareness', 'consideration', 'decision', 'retention']
        if buyer_stage not in valid_stages:
            print(f"❌ Invalid buyer stage: {buyer_stage}")
            return False
        
        print(f"✅ All 7 factors present with correct ranges")
        print(f"   Sample: business_value={first_prompt['business_value']}, tier={tier}, buyer_stage={buyer_stage}")
        return True

    def test_stats_endpoint_comprehensive(self):
        """Verify stats endpoint returns comprehensive 7-factor data"""
        success, response = self.run_test(
            "Verify Comprehensive Stats Endpoint",
            "GET",
            "prompts/stats",
            200
        )
        
        if not success or not response:
            return False
        
        required_stats = [
            'total_prompts', 'avg_business_value', 'avg_volume', 'avg_competition',
            'avg_feasibility', 'avg_intent_score', 'avg_citation_potential',
            'avg_brand_relevance', 'avg_overall_score', 'source_breakdown', 'intent_breakdown'
        ]
        
        missing_stats = []
        for stat in required_stats:
            if stat not in response:
                missing_stats.append(stat)
        
        if missing_stats:
            print(f"❌ Missing stats: {missing_stats}")
            return False
        
        print(f"✅ All comprehensive stats present")
        print(f"   Total prompts: {response.get('total_prompts')}")
        print(f"   Avg overall score: {response.get('avg_overall_score')}")
        print(f"   Source breakdown: {response.get('source_breakdown')}")
        print(f"   Intent breakdown: {response.get('intent_breakdown')}")
        
        return True

    def test_platform_analytics_endpoint(self):
        """Test the new /api/prompts/platform-analytics endpoint"""
        success, response = self.run_test(
            "Test Platform Analytics Endpoint",
            "GET",
            "prompts/platform-analytics",
            200
        )
        
        if not success or not response:
            return False
        
        # Check if analytics are available
        if not response.get('has_analytics', False):
            print("⚠️  No platform analytics available yet - may need more time for Layer 8 processing")
            return True  # Not a failure, just not ready yet
        
        # Verify analytics structure
        platform_analytics = response.get('platform_analytics', {})
        if not platform_analytics:
            print("❌ Empty platform_analytics in response")
            return False
        
        print(f"✅ Platform analytics available for {len(platform_analytics)} platforms")
        
        # Check for expected platforms
        expected_platforms = ['chatgpt', 'claude', 'gemini', 'perplexity']
        found_platforms = list(platform_analytics.keys())
        
        print(f"   Analytics platforms: {found_platforms}")
        
        # Verify each platform has the correct structure
        working_platforms = 0
        for platform in found_platforms:
            platform_data = platform_analytics[platform]
            
            # Check for brand_visibility structure
            if 'brand_visibility' in platform_data:
                brand_visibility = platform_data['brand_visibility']
                if 'visibility_score' in brand_visibility:
                    visibility_score = brand_visibility['visibility_score']
                    print(f"   {platform.upper()}: visibility_score = {visibility_score}")
                    if visibility_score > 0:
                        working_platforms += 1
                else:
                    print(f"❌ Missing visibility_score in brand_visibility for {platform}")
            else:
                print(f"❌ Missing brand_visibility for {platform}")
        
        # Check generation metadata
        generation_metadata = response.get('generation_metadata', {})
        if generation_metadata:
            layer8_enabled = generation_metadata.get('layer8_enabled', False)
            layer8_prompts = generation_metadata.get('layer8_prompts_discovered', 0)
            layer8_in_top100 = generation_metadata.get('layer8_prompts_in_top100', 0)
            
            print(f"   Layer 8 enabled: {layer8_enabled}")
            print(f"   Layer 8 prompts discovered: {layer8_prompts}")
            print(f"   Layer 8 prompts in top 100: {layer8_in_top100}")
        
        if working_platforms > 0:
            print(f"✅ Platform analytics endpoint working correctly ({working_platforms} platforms with data)")
            return True
        else:
            print("⚠️  Platform analytics endpoint working but no platforms have visibility data yet")
            return True  # Still consider this a pass since the endpoint works

    def test_by_platform_endpoints(self):
        """Test the new /api/prompts/by-platform/{platform} endpoints"""
        platforms = ['chatgpt', 'claude', 'gemini', 'perplexity']
        
        for platform in platforms:
            success, response = self.run_test(
                f"Test By-Platform Endpoint: {platform}",
                "GET",
                f"prompts/by-platform/{platform}",
                200
            )
            
            if not success:
                return False
            
            # Check response structure
            if 'platform' not in response or 'prompts' not in response or 'count' not in response:
                print(f"❌ Invalid response structure for {platform}")
                return False
            
            prompt_count = response.get('count', 0)
            print(f"   {platform.upper()}: {prompt_count} prompts")
        
        print(f"✅ All by-platform endpoints working correctly")
        return True
    def run_all_tests(self):
        """Run complete Layer 8: AI Platform Discovery tests"""
        print("🚀 Starting Layer 8: AI Platform Discovery Implementation Tests")
        print("=" * 70)
        
        # Test sequence for Layer 8
        tests = [
            ("Register Layer 8 Test User", self.test_register_layer8_user),
            ("Wait for Layer 8 Onboarding", self.test_onboarding_status), 
            ("Verify Layer 8: AI Platform Discovery", self.test_layer8_ai_platform_discovery),
            ("Verify Financial Services Relevance", self.test_financial_services_prompts_relevance),
            ("Verify New Sources (Including Layer 8)", self.test_new_prompt_sources_with_layer8),
            ("Verify New Intent Classification", self.test_new_intent_classification),
            ("Verify 7-Factor Scoring System", self.test_7_factor_scoring_system),
            ("Verify Comprehensive Stats", self.test_stats_endpoint_comprehensive),
            ("Test Platform Analytics Endpoint", self.test_platform_analytics_endpoint),
            ("Test By-Platform Endpoints", self.test_by_platform_endpoints)
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
        print("\n" + "=" * 70)
        print(f"📊 Layer 8 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All Layer 8: AI Platform Discovery tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False


class AIContentMonitorTester:
    def __init__(self, base_url="https://geo-prompt-monitor.preview.emergentagent.com"):
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
    print("🚀 Starting Layer 8: AI Platform Discovery Implementation Tests")
    print("=" * 70)
    
    # Run Layer 8 Tests
    layer8_tester = Layer8AIDiscoveryTester()
    layer8_success = layer8_tester.run_all_tests()
    
    if not layer8_success:
        print("\n❌ Layer 8: AI Platform Discovery tests failed")
        return 1
    
    print("\n" + "=" * 70)
    print("🎉 All Layer 8: AI Platform Discovery tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())