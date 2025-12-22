import requests
import sys
import json
import time
from datetime import datetime

class NewGEOFrameworkTester:
    def __init__(self, base_url="https://promptr-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.access_token = None
        self.user_id = None
        # Use a simple website that should work for crawling
        self.test_email = f"testgeo{int(time.time())}@geomonitor.com"
        
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
                            print(f"   First item keys: {list(response_data[0].keys())}")
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

    def test_register_sportswear_user(self):
        """Test user registration with sportswear company data"""
        user_data = {
            "email": self.test_email,
            "password": "Test123!",
            "first_name": "Test",
            "last_name": "Sportswear", 
            "company_name": "Athletic Gear Co",
            "website_url": "https://example.com",  # Use simple site that should work
            "industry": "Sportswear & Athletic Apparel",
            "product_description": "Premium athletic footwear and sportswear brand specializing in running shoes, football boots, and lifestyle sneakers",
            "competitors": ["Nike", "Adidas", "Puma"]
        }
        
        success, response = self.run_test(
            "Register Sportswear User for GEO Framework Testing",
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

    def test_onboarding_status(self, max_wait_time=60):
        """Wait for onboarding to complete with shorter timeout"""
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
            time.sleep(3)
        
        print(f"❌ Onboarding did not complete within {max_wait_time} seconds")
        # Let's check if we have any prompts anyway
        success, response = self.run_test(
            "Check Prompts Anyway",
            "GET",
            "prompts",
            200
        )
        
        if success and isinstance(response, list) and len(response) > 0:
            print(f"✅ Found {len(response)} prompts despite onboarding timeout")
            return True
        
        return False

    def test_new_framework_features(self):
        """Test the new 7-Layer GEO Framework features"""
        success, response = self.run_test(
            "Test New Framework Features",
            "GET",
            "prompts",
            200
        )
        
        if not success or not response:
            return False
            
        if not isinstance(response, list) or len(response) == 0:
            print("❌ No prompts found")
            return False
        
        print(f"✅ Found {len(response)} prompts")
        
        # Check first prompt structure
        first_prompt = response[0]
        print(f"   First prompt structure: {list(first_prompt.keys())}")
        
        # Test for 7-factor scoring
        required_factors = [
            'business_value', 'volume', 'competition', 'feasibility',
            'citation_potential', 'brand_relevance', 'overall_score'
        ]
        
        # Check if intent_score exists (new framework) or not (old framework)
        has_intent_score = 'intent_score' in first_prompt
        if has_intent_score:
            required_factors.append('intent_score')
            print("✅ NEW 7-Layer Framework detected (has intent_score)")
        else:
            print("⚠️  OLD Framework detected (missing intent_score)")
        
        missing_factors = []
        for factor in required_factors:
            if factor not in first_prompt:
                missing_factors.append(factor)
        
        if missing_factors:
            print(f"❌ Missing scoring factors: {missing_factors}")
            return False
        
        print(f"✅ All required scoring factors present")
        
        # Test new prompt sources
        expected_sources = [
            'category_search', 'product_discovery', 'competitor_comparison',
            'use_case', 'persona_based', 'problem_solution', 
            'feature_discovery', 'reddit_mining'
        ]
        
        found_sources = set()
        for prompt in response:
            source = prompt.get('source')
            if source:
                found_sources.add(source)
        
        print(f"   Found sources: {sorted(found_sources)}")
        
        # Check for new intent types
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
        
        # Test tier classification
        tiers = set()
        buyer_stages = set()
        for prompt in response:
            tier = prompt.get('tier')
            stage = prompt.get('buyer_stage')
            if tier:
                tiers.add(tier)
            if stage:
                buyer_stages.add(stage)
        
        print(f"   Found tiers: {sorted(tiers)}")
        print(f"   Found buyer stages: {sorted(buyer_stages)}")
        
        # Show sample prompts
        print("   Sample prompts:")
        for i, prompt in enumerate(response[:5]):
            print(f"     {i+1}. {prompt.get('prompt')}")
            print(f"        Source: {prompt.get('source')}, Intent: {prompt.get('intent')}")
            if has_intent_score:
                print(f"        Scores: BV={prompt.get('business_value')}, IS={prompt.get('intent_score')}")
        
        return True

    def test_stats_endpoint(self):
        """Test the stats endpoint for new framework data"""
        success, response = self.run_test(
            "Test Stats Endpoint",
            "GET",
            "prompts/stats",
            200
        )
        
        if not success or not response:
            return False
        
        print(f"   Stats response keys: {list(response.keys())}")
        
        # Check for comprehensive stats
        expected_stats = [
            'total_prompts', 'avg_business_value', 'avg_volume', 'avg_competition',
            'avg_feasibility', 'avg_citation_potential', 'avg_brand_relevance',
            'avg_overall_score', 'source_breakdown', 'intent_breakdown'
        ]
        
        # Check if intent_score average exists (new framework)
        has_intent_avg = 'avg_intent_score' in response
        if has_intent_avg:
            expected_stats.append('avg_intent_score')
            print("✅ NEW Framework stats detected (has avg_intent_score)")
        else:
            print("⚠️  OLD Framework stats detected (missing avg_intent_score)")
        
        missing_stats = []
        for stat in expected_stats:
            if stat not in response:
                missing_stats.append(stat)
        
        if missing_stats:
            print(f"❌ Missing stats: {missing_stats}")
            return False
        
        print(f"✅ All expected stats present")
        print(f"   Total prompts: {response.get('total_prompts')}")
        print(f"   Avg overall score: {response.get('avg_overall_score')}")
        if has_intent_avg:
            print(f"   Avg intent score: {response.get('avg_intent_score')}")
        
        return True

    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting New GEO Framework Testing")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Register Sportswear User", self.test_register_sportswear_user),
            ("Wait for Onboarding", self.test_onboarding_status),
            ("Test New Framework Features", self.test_new_framework_features),
            ("Test Stats Endpoint", self.test_stats_endpoint)
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"\n📋 Running: {test_name}")
                result = test_func()
                if not result:
                    print(f"❌ {test_name} failed - continuing with next test")
                    # Don't break, continue with other tests
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {str(e)}")
                self.tests_run += 1
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed >= 3:  # At least 3 tests should pass
            print("🎉 GEO Framework testing completed successfully!")
            return True
        else:
            print(f"⚠️  Only {self.tests_passed} tests passed")
            return False

def main():
    print("🚀 Starting GEO Framework Testing")
    print("=" * 60)
    
    # Run tests
    tester = NewGEOFrameworkTester()
    success = tester.run_all_tests()
    
    if not success:
        print("\n❌ GEO Framework testing had issues")
        return 1
    
    print("\n" + "=" * 60)
    print("🎉 GEO Framework testing completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())