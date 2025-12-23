# Phase 1: Keyword Monitoring & Recommendations - Testing Guide

## ✅ What's Been Implemented

### 1. Keyword Analysis Engine
- **LLM Questions Discovery**: Uses OpenRouter (GPT-4o) to discover 10 common questions
- **Search Trends**: Uses Tavily API to find most-searched queries
- **Content Coverage Analysis**: Evaluates if your content answers discovered questions

### 2. Template System (6 Templates)
- ✅ Base Template (Universal - all AI models)
- ✅ ChatGPT Template (GPT-4 specific)
- ✅ Perplexity Template (Search-enabled AI)
- ✅ Claude Template (Thoughtful, nuanced)
- ✅ LLaMA Template (Clear, educational)
- ✅ DeepSeek Template (Technical accuracy)

### 3. Comprehensive Recommendations Generator
When you generate recommendations, you get:
- ✅ **Optimized Header**: SEO-friendly H1 title
- ✅ **Subject Line**: Attention-grabbing meta title
- ✅ **Body Improvements**: Section-by-section content enhancements
- ✅ **Credibility Signals**: Author credentials, citations, sources
- ✅ **FAQs**: 3-10 relevant Q&A pairs
- ✅ **Schema Markup**: Structured data recommendations
- ✅ **Semantic Chunking**: Content organization guidance
- ✅ **Keyword Optimization**: LSI keywords, placement tips
- ✅ **Implementation Priority**: Ranked by impact/effort

### 4. "Implement All" Feature
- One-click button to apply ALL recommendations
- Automatically updates content in database
- Shows summary of changes applied

---

## 🧪 How to Test

### Step 1: Login
1. Go to https://geo-prompt-monitor.preview.emergentagent.com
2. Click "Sign In" or "Get Started"
3. Login with your credentials

### Step 2: Access Content Management
1. Navigate to **Content Management** from the dashboard
2. You should see your content list
3. Find content with an **"Optimize"** button

### Step 3: Add Content (If Needed)
If you don't have content:
1. Click **"Add Content"** button
2. Fill in:
   - Title: "Best Treadmills for Home Use in 2025"
   - URL: https://example.com/treadmills
   - Content: "Looking for the best treadmill for your home gym? This guide covers everything..."
3. Click **Submit**

### Step 4: Click "Optimize"
1. Click the **"Optimize"** button (purple, with sparkles icon)
2. You'll be taken to the Content Detail page with 3 tabs:
   - **Overview**: View your content
   - **Keyword Analysis**: Discover questions & trends
   - **Recommendations**: Get AI-powered optimization suggestions

### Step 5: Keyword Analysis
1. Go to **"Keyword Analysis"** tab
2. Enter a keyword (e.g., "Treadmill")
3. Click **"Analyze Keyword"**
4. Wait 10-15 seconds
5. You should see:
   - **LLM Questions**: 10 commonly asked questions with search volume
   - **Most Searched Queries**: Trending searches from the web
   - **Coverage Analysis**: Score showing how well your content answers questions

### Step 6: Generate Recommendations
1. Go to **"Recommendations"** tab
2. Select a template:
   - Start with **"Universal Template (All Models)"**
   - Try model-specific ones (ChatGPT, Perplexity, etc.)
3. Click **"Generate Recommendations"**
4. Wait 15-20 seconds
5. You should see:
   - **Optimized Header**: New H1 suggestion
   - **Subject Line**: SEO title
   - **Body Improvements**: Content enhancements
   - **Credibility Signals**: Sources to add
   - **FAQs**: Question-answer pairs
   - **Keyword Optimization**: Usage tips

### Step 7: Apply Recommendations
1. Review all recommendations
2. Click **"Implement All"** button (big blue button at bottom)
3. Wait 10-15 seconds
4. Success message appears
5. Your content is now optimized!

### Step 8: Verify Changes
1. Go back to Content Management
2. Click on your content again
3. Check the **"Overview"** tab
4. Your content should now include:
   - Optimized title
   - Enhanced content with improvements
   - Better structure

---

## 🔍 Expected Results

### Keyword Analysis Should Show:
```
LLM Questions (10):
1. What is the best treadmill for home use? (high search volume)
2. How much should I spend on a treadmill? (high)
3. Treadmill vs elliptical: which is better? (medium)
... (7 more)

Most Searched Queries (5):
- "best budget treadmills 2025"
- "treadmill buying guide"
... (3 more)

Coverage Analysis:
Score: 65%
Answered: 4 questions
Missing: 6 questions
Recommendations: Add FAQ section, Include price comparisons, etc.
```

### Recommendations Should Include:
```
Optimized Header:
"Top Treadmills for Home Gyms in 2025: Expert Picks & Reviews"

Subject Line:
"Best Treadmills 2025: Expert's Top 10 Picks for Every Budget"

Body Improvements (2-5):
- Introduction: Add hook about fitness goals
- Main Content: Include comparison table
- Features Section: Add expert analysis
...

Credibility Signals (3-5):
- Author Credentials: Add fitness expert bio
- Citations: Link to 3-5 authoritative sources
- Statistics: Include market research data
...

FAQs (3-10):
Q: What features should I look for in a home treadmill?
A: Key features include motor power (2.5+ HP), running surface...

Q: How much should I spend on a good treadmill?
A: Quality home treadmills range from $500-$2000...
...

Keyword Optimization:
- Primary keyword usage: Currently 0.8%, Recommended: 1-2%
- LSI Keywords: treadmill reviews, home gym equipment, cardio machines
- Improvements: Add keyword to first paragraph, Include in H2 tags
```

---

## 🐛 Troubleshooting

### Issue: "Generate Recommendations" button doesn't respond
**Solution**: Wait 15-20 seconds. The API call takes time to process.

### Issue: Recommendations show minimal data
**Solution**: The OpenRouter API might be rate-limited. Fallback recommendations are shown. Try again in a few minutes.

### Issue: Can't see "Optimize" button
**Solution**: Make sure you're logged in and have content created. The button appears in the Actions column.

### Issue: Keyword Analysis fails
**Solution**: Check your internet connection. The Tavily API needs to reach external services.

### Issue: "Implement All" doesn't update content
**Solution**: Check browser console for errors. Ensure you're logged in with valid token.

---

## 📊 API Endpoints (For Advanced Testing)

You can test the backend directly using curl:

### 1. Get Templates
```bash
curl http://localhost:8001/api/templates
```

### 2. Analyze Keyword
```bash
curl -X POST http://localhost:8001/api/keyword-analysis \
  -H "Content-Type: application/json" \
  -d '{"keyword": "Treadmill", "content_id": "YOUR_CONTENT_ID"}'
```

### 3. Generate Recommendations
```bash
curl -X POST "http://localhost:8001/api/content/YOUR_CONTENT_ID/recommendations?template_id=base"
```

### 4. Apply Recommendations
```bash
curl -X POST http://localhost:8001/api/content/YOUR_CONTENT_ID/apply-recommendations \
  -H "Content-Type: application/json" \
  -d '{"content_id": "YOUR_CONTENT_ID", "recommendations": {...}}'
```

---

## ✅ Checklist

Use this checklist to verify everything works:

- [ ] Can login to CiteSight
- [ ] Can access Content Management
- [ ] Can click "Optimize" on content
- [ ] Content Detail page loads with 3 tabs
- [ ] Keyword Analysis tab works
- [ ] Can enter keyword and click "Analyze"
- [ ] See LLM questions (10 items)
- [ ] See search queries (5 items)
- [ ] Coverage analysis shows score
- [ ] Recommendations tab works
- [ ] Can select different templates
- [ ] Click "Generate Recommendations" works
- [ ] See optimized header
- [ ] See subject line
- [ ] See body improvements
- [ ] See credibility signals
- [ ] See FAQs
- [ ] See keyword optimization
- [ ] "Implement All" button visible
- [ ] Clicking "Implement All" works
- [ ] Success message appears
- [ ] Content gets updated

---

## 📝 Notes

- **API Keys**: OpenRouter and Tavily API keys are already configured
- **Rate Limits**: OpenRouter has usage limits. Fallback data is provided if API fails
- **Processing Time**: Recommendations take 15-20 seconds to generate
- **Templates**: Each template provides different optimization strategies
- **Best Practice**: Start with Base template, then try model-specific ones

---

## 🚀 Next Steps (Phase 2 & 3)

Once you confirm Phase 1 works:
- **Phase 2**: Predictive Visibility Score (calculate scores for each AI model)
- **Phase 3**: Competitor Comparison (automatic discovery and scoring)

---

## 💡 Tips

1. **Use Real Keywords**: Try "Treadmill", "Laptop", "Coffee Maker" for best results
2. **Test Different Templates**: Each model has unique optimization strategies
3. **Review Before Applying**: Check recommendations before clicking "Implement All"
4. **Test Multiple Content**: Try with different types of content
5. **Check Coverage Score**: Higher score means content answers more questions

---

For any issues or questions, please let me know!
