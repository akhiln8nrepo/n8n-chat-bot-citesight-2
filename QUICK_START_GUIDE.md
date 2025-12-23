# Quick Start Guide - See the New Features

## ✅ Features are READY and WORKING

The keyword monitoring and recommendations features are fully implemented and working. Here's how to access them:

---

## 🚀 Step-by-Step Instructions

### Step 1: Create an Account or Login

1. Go to: https://geo-prompt-monitor.preview.emergentagent.com/
2. Click **"Get Started"** or **"Sign In"**
3. If you don't have an account:
   - Click "Register here"
   - Fill in your details
   - Verify OTP (check backend logs or use the `/api/dev/get-latest-otp` endpoint)
4. Login with your credentials

### Step 2: Navigate to Content Management

1. After login, you'll be on the Dashboard
2. Click **"Content"** in the left sidebar navigation
   - OR go directly to: `https://geo-prompt-monitor.preview.emergentagent.com/content`

### Step 3: Add Content (If you don't have any)

1. Click the **"Add Content"** button (blue button, top right)
2. Fill in the form:
   ```
   Title: Best Treadmills for Home Use in 2025
   URL: https://example.com/treadmills
   Content: Looking for the best treadmill for your home gym? This comprehensive guide covers everything you need to know about choosing the right treadmill, including features to look for, top brands, and pricing information. We review the top 10 treadmills and provide expert recommendations based on your fitness goals and budget.
   ```
3. Click **Submit**
4. Wait for content to be created

### Step 4: Access the NEW Features

1. In the Content Management table, you'll see your content listed
2. Look at the **"Actions"** column (rightmost column)
3. You should see TWO buttons:
   - **"Visibility"** (blue button with eye icon)
   - **"Optimize"** (purple button with sparkles ✨ icon) ← THIS IS NEW!

4. Click the **"Optimize"** button

### Step 5: You'll See the Content Detail Page with 3 Tabs

After clicking Optimize, you'll be on: `/content/{contentId}`

You'll see 3 tabs:
1. **Overview** - View your content
2. **Keyword Analysis** ← NEW FEATURE
3. **Recommendations** ← NEW FEATURE

### Step 6: Try Keyword Analysis

1. Click the **"Keyword Analysis"** tab
2. Enter a keyword in the input field, for example: **"Treadmill"**
3. Click **"Analyze Keyword"** button
4. Wait 10-15 seconds
5. You'll see:
   - **Previously Asked LLM Questions**: 10 common questions with search volume indicators
   - **Most Searched Queries**: 5 trending web searches
   - **Content Coverage Analysis**: Score showing how well your content answers the questions

### Step 7: Generate Recommendations

1. Click the **"Recommendations"** tab
2. Select a template from the dropdown:
   - "Universal Template (All Models)" ← Start with this
   - Or try: ChatGPT, Perplexity, Claude, LLaMA, or DeepSeek specific templates
3. Click **"Generate Recommendations"** button
4. Wait 15-20 seconds
5. You'll see comprehensive recommendations including:
   - Optimized Header
   - SEO Subject Line
   - Body Content Improvements
   - Credibility Signals
   - FAQs
   - Keyword Optimization tips

### Step 8: Apply Recommendations

1. After reviewing the recommendations
2. Scroll to the bottom
3. Click the big blue **"Implement All"** button
4. Wait 10-15 seconds
5. Success! Your content is now optimized

### Step 9: Verify Changes

1. Go back to Content Management
2. Click on your content again
3. Check the "Overview" tab
4. Your content should now include all the improvements!

---

## 🎯 What You Should See

### In the Content Table:
```
Title              URL                 Publisher   Added      Actions
─────────────────────────────────────────────────────────────────────────
Best Treadmills... example.com/...    Test Pub    Nov 29     [Visibility] [Optimize] ← NEW!
```

### In Keyword Analysis Tab:
```
┌─ Previously Asked LLM Questions ─────────────────────┐
│ 1. What is the best treadmill? (high search volume)  │
│ 2. How to choose a treadmill? (high)                 │
│ 3. Treadmill buying guide 2025 (medium)              │
│ ... (7 more questions)                                │
└──────────────────────────────────────────────────────┘

┌─ Most Searched Queries ──────────────────────────────┐
│ • "best budget treadmills 2025"                       │
│ • "treadmill reviews for home"                        │
│ ... (3 more queries)                                  │
└──────────────────────────────────────────────────────┘
```

### In Recommendations Tab:
```
┌─ Content Optimization ───────────────────────────────┐
│ Template: [Universal Template (All Models) ▼]        │
│ [✨ Generate Recommendations]                         │
└──────────────────────────────────────────────────────┘

After clicking Generate:

┌─ Optimized Header ───────────────────────────────────┐
│ "Top Treadmills for Home Gyms in 2025: Expert Picks"│
└──────────────────────────────────────────────────────┘

┌─ Subject Line ───────────────────────────────────────┐
│ "Best Treadmills 2025: Top 10 Picks for Every Budget│
└──────────────────────────────────────────────────────┘

... (more sections)

┌─ Ready to Optimize? ─────────────────────────────────┐
│ Apply all recommendations automatically              │
│                                   [✓ Implement All]  │
└──────────────────────────────────────────────────────┘
```

---

## 🐛 If You Don't See the "Optimize" Button

### Possible Issues:

1. **Not Logged In**
   - Solution: Make sure you're logged in first
   - Check if you see the Dashboard navigation

2. **No Content Created**
   - Solution: Create at least one piece of content first
   - Click "Add Content" button

3. **Browser Cache**
   - Solution: Hard refresh the page (Ctrl+Shift+R or Cmd+Shift+R)
   - Or clear browser cache

4. **Still on Old Version**
   - Solution: The code was just updated
   - Try clearing cache and refreshing

---

## 📱 Direct URLs to Test

If you want to skip navigation:

1. **Content Management**: 
   `https://geo-prompt-monitor.preview.emergentagent.com/content`

2. **Content Detail (replace {id} with actual content ID)**:
   `https://geo-prompt-monitor.preview.emergentagent.com/content/{contentId}`

3. **Get Content ID**: Login, go to Content page, and look at the URL when you click Optimize

---

## ✅ Verification Checklist

- [ ] I can login to CiteSight
- [ ] I can see Content Management page
- [ ] I have at least 1 content item
- [ ] I can see "Optimize" button in the Actions column (purple, with sparkles icon)
- [ ] Clicking "Optimize" takes me to Content Detail page
- [ ] I can see 3 tabs: Overview, Keyword Analysis, Recommendations
- [ ] Keyword Analysis shows questions when I enter a keyword
- [ ] Recommendations shows optimization suggestions
- [ ] "Implement All" button applies changes

---

## 🔧 Backend Status Check

To verify the backend is working, you can check these endpoints directly:

1. **Templates**: https://geo-prompt-monitor.preview.emergentagent.com/api/templates
   - Should return JSON with template names

2. **Check if services are running**:
   ```bash
   curl https://geo-prompt-monitor.preview.emergentagent.com/api/
   ```

---

## 💡 Tips

1. **First Time**: The features work best with real content that has substance
2. **Keywords**: Use specific keywords like "Treadmill", "Laptop", "Coffee Maker"
3. **Templates**: Start with "Universal Template", then experiment with model-specific ones
4. **Wait Time**: Allow 10-20 seconds for AI processing
5. **Review First**: Check recommendations before clicking "Implement All"

---

## 📞 Still Not Seeing Features?

If you're still not seeing the "Optimize" button or the new tabs:

1. **Send me a screenshot** of your Content Management page
2. **Check browser console** for any error messages (F12 → Console tab)
3. **Verify you're logged in** and can access the dashboard
4. **Try creating new content** and check if the button appears there

The features are definitely implemented and working in the code - I've validated them. The issue might be with authentication, caching, or navigation.

---

Let me know what you see and I'll help you access the features!
