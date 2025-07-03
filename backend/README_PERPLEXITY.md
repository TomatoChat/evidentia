# Perplexity AI Integration for Evidentia

## Overview

This integration adds **Perplexity AI** capabilities to Evidentia alongside the existing OpenAI functionality. Perplexity AI provides real-time web search and analysis capabilities, making it ideal for brand research and competitive intelligence.

## Key Features

### 🔍 **Real-Time Web Search**
- Access to current web information (vs. training data cutoffs)
- Automatic citation and source tracking
- High-quality search results with relevance scoring

### 🏢 **Enhanced Brand Analysis**
- Live competitor monitoring
- Real-time sentiment analysis
- Current market trend identification
- Social media activity tracking

### 📊 **Query Generation with Context**
- Web-aware query suggestions
- Industry-specific search patterns
- Competitor-informed queries

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/perplexity-generate-queries` | POST | Generate brand analysis queries using Perplexity |
| `/perplexity-web-search` | POST | Perform web search and analysis |
| `/perplexity-brand-analysis` | POST | Comprehensive brand analysis with real-time data |
| `/stream-perplexity-search` | POST | Streaming web search with real-time updates |

### Request Examples

#### Generate Queries
```bash
curl -X POST http://localhost:5000/perplexity-generate-queries \
  -H "Content-Type: application/json" \
  -d '{
    "brandName": "Tesla",
    "brandCountry": "United States",
    "brandDescription": "Electric vehicle manufacturer",
    "brandIndustry": "Automotive",
    "totalQueries": 10
  }'
```

#### Web Search & Analysis
```bash
curl -X POST http://localhost:5000/perplexity-web-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tesla stock performance Q4 2024",
    "context": "Financial analysis for investment research"
  }'
```

#### Brand Analysis
```bash
curl -X POST http://localhost:5000/perplexity-brand-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "brandName": "Netflix",
    "brandWebsite": "https://netflix.com",
    "competitors": ["Disney+", "Hulu", "Amazon Prime Video"]
  }'
```

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install requests
```

### 2. Get Perplexity API Key
1. Visit [Perplexity AI](https://www.perplexity.ai/) 
2. Sign up for an API account
3. Generate an API key from your dashboard

### 3. Set Environment Variable
```bash
# Add to your .env file or export directly
export PERPLEXITY_API_KEY="your-perplexity-api-key-here"
```

### 4. Test the Integration
```bash
cd backend
python examples/perplexity_example.py
```

## Code Usage

### Python Integration

```python
import libs.perplexity as perplexityAnalytics

# Generate queries with real-time web context
queries = perplexityAnalytics.getCoherentQueries(
    brandName="Tesla",
    brandCountry="United States", 
    brandDescription="Electric vehicle company",
    brandIndustry="Automotive",
    totalQueries=10
)

# Perform web search and analysis
results = perplexityAnalytics.webSearchAndAnalyze(
    query="Tesla latest news 2024",
    context="Looking for recent developments"
)

# Get comprehensive brand analysis
analysis = perplexityAnalytics.getBrandAnalysis(
    brandName="Netflix",
    brandWebsite="https://netflix.com",
    competitors=["Disney+", "Hulu"]
)
```

## OpenAI vs Perplexity Comparison

| Feature | OpenAI | Perplexity |
|---------|--------|------------|
| **Data Freshness** | Training cutoff | Real-time web |
| **Citations** | No direct citations | Automatic source citations |
| **Web Search** | Requires separate tools | Built-in web search |
| **Response Speed** | Fast | Moderate (due to web search) |
| **Cost** | Lower per query | Higher per query |
| **Best Use Case** | General analysis | Research & current events |

## Response Formats

### Query Generation Response
```json
{
  "queries": [
    "Tesla Model 3 vs competitors 2024",
    "Tesla charging network expansion",
    "Tesla stock analysis latest quarter"
  ],
  "source": "perplexity"
}
```

### Web Search Response
```json
{
  "summary": "Tesla's Q4 2024 performance shows...",
  "key_insights": [
    "Revenue increased 15% year-over-year",
    "Model Y sales exceeded projections",
    "Charging network expanded to 50,000 stations"
  ],
  "sources": [
    {
      "title": "Tesla Q4 2024 Earnings Report",
      "url": "https://example.com/tesla-earnings",
      "snippet": "Tesla reported record quarterly revenue..."
    }
  ],
  "search_quality": "high",
  "last_updated": "recent",
  "perplexity_citations": {...},
  "model_used": "llama-3.1-sonar-large-128k-online"
}
```

### Brand Analysis Response
```json
{
  "brand_name": "Netflix",
  "overall_sentiment": "positive",
  "market_position": "Leading streaming platform with strong content portfolio",
  "reputation_score": "8/10",
  "recent_developments": [
    "Launched ad-supported tier",
    "Expanded into gaming content",
    "New international partnerships"
  ],
  "competitive_analysis": {
    "strengths": ["Content library", "Global reach", "Technology platform"],
    "weaknesses": ["Increasing competition", "Content costs"],
    "opportunities": ["Gaming expansion", "International growth"],
    "threats": ["Disney+ growth", "Economic downturn impact"]
  },
  "digital_presence": {
    "website_quality": "high",
    "social_media_activity": "active",
    "content_strategy": "Multi-platform content marketing"
  },
  "perplexity_citations": {...},
  "analysis_timestamp": "current"
}
```

## Error Handling

The integration includes comprehensive error handling:

- **API Key Missing**: Clear error messages with setup instructions
- **Rate Limiting**: Graceful degradation with retry logic
- **Network Issues**: Fallback responses with error context
- **Invalid Responses**: JSON parsing protection with error reporting

## Best Practices

### 1. **API Key Security**
- Never commit API keys to version control
- Use environment variables or secure key management
- Rotate keys regularly

### 2. **Cost Management**
- Monitor API usage through Perplexity dashboard
- Implement caching for repeated queries
- Use appropriate query complexity

### 3. **Performance Optimization**
- Consider response time vs. data freshness trade-offs
- Implement async processing for long-running analyses
- Cache results when appropriate

### 4. **Error Recovery**
- Implement fallback to OpenAI when Perplexity fails
- Log errors for debugging and monitoring
- Provide meaningful error messages to users

## Troubleshooting

### Common Issues

**1. `PERPLEXITY_API_KEY environment variable is not set`**
```bash
# Solution: Set your API key
export PERPLEXITY_API_KEY="your-key-here"
```

**2. `ModuleNotFoundError: No module named 'requests'`**
```bash
# Solution: Install requests
pip install requests
```

**3. API Rate Limiting**
- Check your Perplexity account usage limits
- Implement exponential backoff for retries
- Consider upgrading your Perplexity plan

**4. JSON Parsing Errors**
- Usually caused by API response format changes
- Check logs for raw response content
- Verify API key permissions

## Support

For issues specific to this integration:
1. Check the example file: `backend/examples/perplexity_example.py`
2. Review server logs for detailed error messages
3. Verify API key permissions in Perplexity dashboard
4. Test with simple queries first before complex brand analysis

## License

This integration follows the same license as the main Evidentia project.