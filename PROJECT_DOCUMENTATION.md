# GEO Monitor - AI Content Visibility Monitoring Platform

## Overview
GEO Monitor is a comprehensive platform that enables publishers to monitor their content presence in AI-generated summaries across major platforms (Google AI Overviews, Bing Copilot, Perplexity, ChatGPT). The platform provides actionable GEO (Generative Engine Optimization) recommendations to improve AI visibility and includes competitive intelligence features.

## Features

### MVP Features (Implemented)
1. **AI Summary Visibility Tracker**
   - Track content presence across 4 major AI platforms
   - View visibility scores (0-100) for each platform
   - Monitor content position in AI summaries
   - Real-time tracking status

2. **Keyword Monitoring**
   - Add keywords to track across AI platforms
   - See which platforms feature your keywords
   - Track average keyword positions
   - Filter keywords by content

3. **GEO Recommendations**
   - AI-powered recommendations using Emergent LLM (GPT-4o-mini)
   - Priority-based recommendations (High, Medium, Low)
   - Categories: Semantic Chunking, Schema Markup, FAQ Injection, Content Structure, Keyword Optimization
   - Content-specific analysis

4. **Dashboard with Analytics**
   - Total content tracked
   - Average visibility score
   - Keywords monitored
   - Platforms present count
   - 7-day visibility trend chart
   - Platform presence breakdown

5. **Competitor Analysis**
   - Compare visibility against competitors
   - GEO Health Score for competitors
   - Platform presence comparison
   - Competitive insights and recommendations

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB (Motor async driver)
- **AI Integration**: Emergent LLM (OpenAI GPT-4o-mini)
- **API Design**: RESTful with `/api` prefix

### Frontend
- **Framework**: React 19
- **Router**: React Router v7
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI (shadcn/ui)
- **Icons**: Lucide React
- **Notifications**: Sonner
- **HTTP Client**: Axios

### Design System
- **Fonts**: 
  - Headings: Space Grotesk
  - Body: Inter
- **Color Scheme**: Light background with ocean blue/teal accents
- **Style**: Modern, clean, analytics-focused

## Architecture

### Database Schema

#### Publishers Collection
```json
{
  "id": "uuid",
  "name": "string",
  "email": "string",
  "website": "string",
  "created_at": "datetime"
}
```

#### Content Collection
```json
{
  "id": "uuid",
  "publisher_id": "uuid",
  "title": "string",
  "url": "string",
  "content_text": "string",
  "created_at": "datetime"
}
```

#### Visibility Collection
```json
{
  "id": "uuid",
  "content_id": "uuid",
  "platform": "string",
  "visibility_score": "float (0-100)",
  "is_present": "boolean",
  "summary_snippet": "string",
  "position": "integer",
  "checked_at": "datetime"
}
```

#### Keywords Collection
```json
{
  "id": "uuid",
  "content_id": "uuid",
  "keyword": "string",
  "platforms_found": ["array of strings"],
  "avg_position": "float",
  "created_at": "datetime"
}
```

#### Recommendations Collection
```json
{
  "id": "uuid",
  "content_id": "uuid",
  "recommendation_type": "string",
  "recommendation_text": "string",
  "priority": "string (high/medium/low)",
  "created_at": "datetime"
}
```

### API Endpoints

#### Publishers
- `POST /api/publishers` - Create publisher
- `GET /api/publishers` - Get all publishers

#### Content
- `POST /api/content` - Add content (triggers visibility tracking & recommendations)
- `GET /api/content` - Get all content
- `GET /api/content/{content_id}` - Get specific content

#### Visibility
- `GET /api/visibility/{content_id}` - Get visibility data for content

#### Keywords
- `POST /api/keywords` - Add keyword to track
- `GET /api/keywords/{content_id}` - Get keywords for content

#### Recommendations
- `GET /api/recommendations/{content_id}` - Get GEO recommendations

#### Dashboard
- `GET /api/dashboard/stats?publisher_id={id}` - Get dashboard statistics

#### Competitors
- `GET /api/competitors?publisher_id={id}` - Get competitor analysis

## Frontend Routes

- `/` - Landing page with hero and features
- `/dashboard` - Main dashboard with metrics
- `/content` - Content management
- `/keywords` - Keyword monitoring
- `/recommendations` - GEO recommendations
- `/competitors` - Competitor analysis

## Data Flow

### Adding Content
1. User creates publisher (if not exists)
2. User adds content with title, URL, and text
3. Backend automatically:
   - Generates mock visibility data for all 4 AI platforms
   - Calls Emergent LLM to generate GEO recommendations
   - Stores everything in MongoDB
4. Frontend displays confirmation

### Viewing Analytics
1. Dashboard fetches stats from backend
2. Backend aggregates data from MongoDB
3. Calculates visibility scores, trends, platform presence
4. Returns formatted data for visualization
5. Frontend renders charts and metrics

## Mock Data Strategy

Since actual AI platform APIs are not integrated (as per MVP scope), the system uses:
- **Visibility Data**: Randomly generated scores (45-95 for present, 5-30 for not present)
- **Platform Presence**: 66% chance of being present on each platform
- **Keyword Tracking**: Random platform selection from available platforms
- **Competitor Data**: Hardcoded examples (TechCrunch, The Verge, Wired)

## AI Integration

### Emergent LLM Setup
- **Model**: OpenAI GPT-4o-mini
- **Key**: EMERGENT_LLM_KEY (universal key for OpenAI, Anthropic, Gemini)
- **Usage**: GEO recommendation generation
- **Library**: emergentintegrations (custom library)

### Recommendation Generation
```python
chat = LlmChat(
    api_key=EMERGENT_LLM_KEY,
    session_id=f"geo_rec_{content_id}",
    system_message="GEO expert prompt..."
).with_model("openai", "gpt-4o-mini")

response = await chat.send_message(user_message)
```

## Environment Variables

### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
CORS_ORIGINS=*
EMERGENT_LLM_KEY=sk-emergent-eB71bBd312f376b820
```

### Frontend (.env)
```
REACT_APP_BACKEND_URL=https://citesight-demo.preview.emergentagent.com
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
```

## Development

### Running Locally
Both services are managed by supervisor and support hot reload:

```bash
# Check status
sudo supervisorctl status

# Restart services
sudo supervisorctl restart backend frontend

# View logs
tail -f /var/log/supervisor/backend.*.log
tail -f /var/log/supervisor/frontend.*.log
```

### Installing Dependencies

#### Backend
```bash
cd /app/backend
pip install -r requirements.txt
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

#### Frontend
```bash
cd /app/frontend
yarn install
```

## Testing

Comprehensive test suite covers:
- All 13 backend API endpoints
- Frontend UI components
- Form validation and submission
- Navigation flows
- Data display and visualization
- Modal interactions
- Integration between frontend and backend

Run tests:
```bash
python3 /app/backend_test.py
```

## Future Enhancements (Post-MVP)

### Extended Features
1. **Real AI Platform Integration**
   - Connect to actual Google AI Overview API
   - Integrate Bing Copilot tracking
   - Add Perplexity API integration
   - Connect ChatGPT search API

2. **Predictive GEO Scoring**
   - ML model to predict visibility changes
   - ROI impact analysis
   - Trend forecasting

3. **Real-Time Alerts**
   - Email notifications for visibility changes
   - Slack/Discord webhooks
   - Custom alert thresholds

4. **Attribution & Micro-Payment API**
   - Track content usage in AI responses
   - Monetization framework
   - Payment processing integration

5. **AI Content Syndication**
   - Push content to chatbots
   - Voice assistant integration
   - API for content distribution

## Performance Considerations

- **Caching**: Consider Redis for frequently accessed data
- **Batch Processing**: Queue system for visibility checks
- **Rate Limiting**: Implement for API protection
- **Database Indexing**: Add indexes on frequently queried fields

## Security

- CORS configured for production domain
- Environment variables for sensitive data
- Input validation on all endpoints
- MongoDB connection secured

## Deployment

Platform is deployed on Emergent's infrastructure:
- **URL**: https://citesight-demo.preview.emergentagent.com
- **Backend**: Port 8001 (internal), proxied via Kubernetes ingress
- **Frontend**: Port 3000 (internal)
- **MongoDB**: Local instance on port 27017

## Support

For issues or questions about the platform, refer to the implementation files:
- Backend logic: `/app/backend/server.py`
- Frontend components: `/app/frontend/src/components/`
- Testing: `/app/backend_test.py`

---

**Built with Emergent AI Platform**
