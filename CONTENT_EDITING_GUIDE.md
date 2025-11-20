# CiteSight Website Content Editing Guide

## 📝 How to Edit Content on Different Pages

All website content is stored in easily editable React component files. Here's where to find and edit content for each page:

---

## 🏠 HOME PAGE
**File Location:** `/app/frontend/src/pages/Home.js`

### What You Can Edit:

#### Hero Section (Lines 40-90)
```javascript
<h1>Optimize Your Content for the <span>AI Era</span></h1>
<p>Track, analyze, and improve your content visibility...</p>
```
**Edit:** Main headline, subheadline, button text

#### Features Section (Lines 15-35)
```javascript
const features = [
  {
    icon: <TrendingUp size={28} />,
    title: 'AI Summary Visibility Tracker',
    description: 'Monitor your content presence across...'
  },
  // Add more features here
];
```
**Edit:** Feature titles, descriptions, icons

#### Testimonials (Lines 37-55)
```javascript
const testimonials = [
  {
    name: 'Sarah Chen',
    role: 'Head of Content, TechFlow Media',
    content: 'CiteSight helped us increase...',
    rating: 5
  },
  // Add more testimonials
];
```
**Edit:** Customer names, roles, testimonial text

#### Pricing Preview (Lines 57-75)
```javascript
const pricingPreview = [
  {
    name: 'Starter',
    price: '$99',
    description: 'Perfect for small publishers',
    features: ['Up to 50 pages tracked', ...]
  },
];
```
**Edit:** Plan names, prices, features list

---

## ℹ️ ABOUT PAGE
**File Location:** `/app/frontend/src/pages/About.js`

### What You Can Edit:

#### Mission & Vision (Lines 40-70)
```javascript
<h2>Our Mission</h2>
<p>To empower publishers and content creators...</p>

<h2>Our Vision</h2>
<p>A world where content creators can seamlessly adapt...</p>
```

#### Founding Story (Lines 90-120)
```javascript
<div className="prose prose-lg">
  <p>CiteSight was born from a simple observation...</p>
  <p>In early 2024, our founders—seasoned SEO experts...</p>
</div>
```

#### Team Members (Lines 25-35)
```javascript
const team = [
  { 
    name: 'Sarah Mitchell', 
    role: 'CEO & Co-Founder', 
    bio: 'Former Head of SEO at TechCorp...' 
  },
  // Add/edit team members
];
```

---

## ⚡ FEATURES PAGE
**File Location:** `/app/frontend/src/pages/Features.js`

### What You Can Edit:

#### Feature Details (Lines 15-120)
```javascript
const features = [
  {
    icon: <TrendingUp size={40} />,
    title: 'AI Summary Visibility Tracker',
    description: 'Track where and when your content appears...',
    benefits: [
      'Real-time monitoring across Google AI...',
      'Visibility score (0-100) for each platform',
      // Add more benefits
    ]
  },
  // Add more features
];
```

---

## 💰 PRICING PAGE
**File Location:** `/app/frontend/src/pages/Pricing.js`

### What You Can Edit:

#### Pricing Plans (Lines 10-60)
```javascript
const plans = [
  {
    name: 'Starter',
    description: 'Perfect for small publishers',
    monthlyPrice: 99,
    annualPrice: 990,
    features: [
      { name: 'Up to 50 pages tracked', included: true },
      { name: 'Basic GEO recommendations', included: true },
      // Add more features
    ]
  },
  // Add more plans
];
```

#### FAQ Section (Lines 65-95)
```javascript
const faqs = [
  {
    question: 'Can I change plans later?',
    answer: 'Yes! You can upgrade or downgrade...'
  },
  // Add more FAQs
];
```

---

## 📞 CONTACT PAGE
**File Location:** `/app/frontend/src/pages/Contact.js`

### What You Can Edit:

#### Contact Information (Lines 60-90)
```javascript
<div>
  <h3>Email</h3>
  <p>hello@citesight.com</p>
  <p>support@citesight.com</p>
</div>

<div>
  <h3>Phone</h3>
  <p>+1 (555) 123-4567</p>
</div>

<div>
  <h3>Office</h3>
  <p>123 Innovation Drive</p>
  <p>San Francisco, CA 94105</p>
</div>
```

---

## 🎨 STYLING & BRANDING

### Colors
**File Location:** `/app/frontend/src/App.css`

```css
/* Main Brand Colors */
.bg-blue-600 { /* Primary Blue: #2563eb */ }
.text-slate-900 { /* Dark Text: #0f172a */ }

/* Change colors by finding and replacing in CSS */
```

### Logo & Brand Name
**Files to Update:**
- `/app/frontend/src/components/MarketingNav.js` (Line 30)
- `/app/frontend/src/components/Navigation.js` (Line 40)
- `/app/frontend/src/components/MarketingFooter.js` (Line 15)

```javascript
<span className="text-2xl font-bold">CiteSight</span>
// Change "CiteSight" to your brand name
```

### Fonts
**File Location:** `/app/frontend/src/App.css` (Lines 1-10)

```css
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* Change to your preferred fonts */
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; }
body { font-family: 'Inter', sans-serif; }
```

---

## 🖼️ IMAGES

### Replace Images
Find image URLs in component files and replace with your own:

```javascript
// Example in Home.js
<img 
  src="https://images.unsplash.com/photo-1551288049-bebda4e38f71" 
  alt="Dashboard" 
/>

// Replace with your image URL or path
<img 
  src="/images/your-dashboard.png" 
  alt="Dashboard" 
/>
```

### Add Images to Project
1. Create folder: `/app/frontend/public/images/`
2. Add your images there
3. Reference as: `/images/your-image.png`

---

## 🔄 HOW TO APPLY CHANGES

### Method 1: Using View & Edit Tools
1. Open file using: `view_file` tool
2. Find the section you want to edit
3. Use `search_replace` tool to update content
4. Changes auto-reload (hot reload enabled)

### Method 2: Direct File Editing
1. Navigate to file location
2. Edit the content directly
3. Save the file
4. Frontend automatically reloads

### Method 3: Using Bulk Updates
For multiple changes across files, use bulk operations.

---

## 📋 COMMON EDITING TASKS

### Change Hero Headline
**File:** `/app/frontend/src/pages/Home.js`
**Line:** ~55
```javascript
// Find this:
<h1>Optimize Your Content for the <span>AI Era</span></h1>

// Change to:
<h1>Your Custom Headline Here</h1>
```

### Update Company Email
**File:** `/app/frontend/src/pages/Contact.js`
**Line:** ~70
```javascript
// Find this:
<p>hello@citesight.com</p>

// Change to:
<p>your-email@yourcompany.com</p>
```

### Modify Pricing
**File:** `/app/frontend/src/pages/Pricing.js`
**Line:** ~15
```javascript
// Find this:
monthlyPrice: 99,

// Change to:
monthlyPrice: 149,
```

### Update Footer Links
**File:** `/app/frontend/src/components/MarketingFooter.js`
**Line:** ~40-80
```javascript
// Edit navigation links and social media URLs
```

---

## 🚀 DEPLOYMENT AFTER EDITING

### For Preview Environment
Changes are live immediately (hot reload enabled).

### For Production Deployment
1. Test all changes in preview
2. Click "Deploy" button in Emergent
3. Wait ~10 minutes for deployment
4. Changes go live on your production domain

---

## ⚠️ IMPORTANT NOTES

### Don't Edit These Files:
- `/app/backend/server.py` - Backend logic
- `/app/backend/auth_routes.py` - Authentication
- `/app/frontend/src/utils/axios.js` - API configuration

### Safe to Edit:
- All `/app/frontend/src/pages/*.js` files
- `/app/frontend/src/components/MarketingNav.js`
- `/app/frontend/src/components/MarketingFooter.js`
- `/app/frontend/src/App.css`

### After Major Changes:
```bash
# Restart frontend to ensure changes apply
sudo supervisorctl restart frontend
```

---

## 🆘 NEED HELP?

### Quick Reference:
- **Home Page Content**: `/app/frontend/src/pages/Home.js`
- **Styles/Colors**: `/app/frontend/src/App.css`
- **Navigation**: `/app/frontend/src/components/MarketingNav.js`
- **Footer**: `/app/frontend/src/components/MarketingFooter.js`

### Testing Changes:
1. Make edit
2. Save file
3. Refresh browser (changes auto-reload)
4. If no change, restart: `sudo supervisorctl restart frontend`

---

**Remember:** Always test changes in preview before deploying to production!
