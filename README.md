# Evidentia - Generative Engine Optimization (GEO) Tool

🤖 A modern full-stack GEO analysis platform with React frontend and Flask API backend that helps brands understand their positioning in LLM responses.

## Architecture

- **Frontend**: Modern React/Next.js app with Tailwind CSS
- **Backend**: Flask API server with streaming capabilities  
- **Deployment**: Frontend ready for Vercel, backend for any Python hosting

## What is GEO?

**Generative Engine Optimization (GEO)** is the practice of optimizing content and brand positioning for Large Language Models (LLMs) and AI-powered responses, rather than traditional search engines.

## ⚡ Quick Start (One Command!)

```bash
# Install everything and start both servers
npm run install:all && npm run dev
```

This will:
- Install Python backend dependencies
- Install Node.js frontend dependencies  
- Start Flask API server on port 5000
- Start React frontend on port 3000

## 🚀 Individual Commands

### Development
```bash
# Start both frontend and backend
npm run dev

# Or start individually:
npm run start:backend    # Flask API (port 5000)
npm run start:frontend   # React app (port 3000)
```

### Installation
```bash
npm run install:all      # Install both frontend and backend deps
npm run install:backend  # Python dependencies only
npm run install:frontend # Node.js dependencies only
```

### Production
```bash
npm run build:frontend   # Build for production
npm run start:prod       # Start production build
```

## 📁 Project Structure

```
evidentia/
├── frontend/              # 🌐 React/Next.js Frontend
│   ├── app/              # Next.js 13+ app directory
│   ├── components/       # React components
│   ├── package.json      # Frontend dependencies
│   └── tailwind.config.js
├── libs/                 # 🧠 Core analysis libraries
│   ├── geo_analysis.py   # GEO analysis engine
│   ├── openai.py        # OpenAI API integration
│   └── utils.py         # Brand analysis utilities
├── server.py            # 🔌 Flask API server
├── requirements.txt     # Python dependencies
├── package.json         # Root project scripts
└── start-dev.sh         # Development startup script
```

## 🎯 Features

### Core Analysis Capabilities
- **🧠 Advanced LLM Brand Analysis**: Multi-model AI analysis
- **📊 Multi-Model GEO Testing**: Test across GPT-4, GPT-3.5, etc.
- **💭 Intelligent Query Generation**: AI-powered test queries
- **🎯 Sentiment & Positioning Analysis**: Brand sentiment scoring
- **🥊 Competitive Intelligence**: Competitor analysis
- **📈 Performance Metrics**: Comprehensive analytics

### Modern Frontend
- **⚡ Two-step Landing Page**: Email collection → Brand analysis
- **📱 Responsive Design**: Works on all devices
- **🎨 Modern UI**: Tailwind CSS with gradient backgrounds
- **🔄 Real-time Updates**: Streaming API responses
- **🚀 Ready for Vercel**: Optimized for deployment

### API Backend
- **🔌 RESTful API**: Clean API endpoints
- **📡 Streaming Support**: Real-time progress updates
- **🌐 CORS Enabled**: Frontend-backend separation
- **⚡ Fast Responses**: Optimized performance

### 🔌 API Endpoints

#### 📊 Streaming Brand Analysis (Recommended)
```bash
POST /stream-brand-info
Content-Type: application/json

{
  "brandName": "jethr",
  "brandWebsite": "jethr.com",
  "brandCountry": "italy"
}
```
Returns real-time streaming updates with progress tracking.

#### 📝 Streaming Query Generation
```bash
POST /stream-generate-queries
Content-Type: application/json

{
  "brandName": "Company Name",
  "brandCountry": "italy",
  "brandDescription": "Company description...",
  "brandIndustry": "Technology",
  "totalQueries": 10
}
```
Returns streaming progress updates during query generation.

#### 🌍 Advanced GEO Analysis (Streaming)
```bash
POST /stream-test-queries
Content-Type: application/json

{
  "brandName": "Company Name",
  "queries": ["What are the best tech companies?", "Recommend software tools"],
  "competitors": ["Competitor1", "Competitor2"],
  "models": ["gpt-4o-mini-2024-07-18", "gpt-3.5-turbo"]
}
```
Returns comprehensive streaming GEO analysis with real-time progress updates.

#### 🤖 Available LLM Models
```bash
GET /get-llm-models
```
Returns list of available LLM models for testing.

#### 💡 LLM Suggestions
```bash
POST /get-llm-suggestions
Content-Type: application/json

{
  "brandName": "Company Name",
  "industry": "Technology"
}
```

#### 🔍 Web Search & Analysis
```bash
POST /web-search
Content-Type: application/json

{
  "query": "latest trends in AI automation tools",
  "context": "small business market analysis"
}
```
Returns structured web search results with analysis and insights.

#### ⚡ Streaming Web Search
```bash
POST /stream-web-search
Content-Type: application/json

{
  "query": "competitor analysis for tech companies",
  "context": "market positioning research"
}
```
Returns real-time streaming web search with progress updates.

#### Legacy Endpoints (Non-Streaming)
```bash
POST /brand-info          # Basic brand information
POST /generate-queries    # Generate test queries
POST /test-queries       # Basic GEO analysis
GET /health             # Health check
```

### 🔍 Web Search Integration

The platform now includes advanced web search capabilities powered by OpenAI's Responses API:

- **Real-time web search** with current market data
- **Structured analysis** of search results with insights and sources
- **Quality assessment** of search information (high/medium/low)
- **Source attribution** with URLs and relevant excerpts
- **Streaming progress** updates during search operations

### Jupyter Notebook

You can also use the functionality directly in Jupyter notebooks:

```python
import libs.utils as utils
import libs.openai as openaiAnalytics

# Get brand information
brand_info = utils.getCompanyInfo("jethr", "jethr.com", "italy")

# Generate queries
queries = openaiAnalytics.getCoherentQueries(
    brand_info['name'], 
    "italy", 
    brand_info['description'], 
    brand_info['industry'], 
    10
)

# Perform web search and analysis
search_results = openaiAnalytics.webSearchAndAnalyze(
    "latest AI automation trends 2024",
    "market research for technology companies"
)
```

## 📁 Project Structure

```
evidentia/
├── libs/                   # Core analysis libraries
│   ├── geo_analysis.py     # 🌍 GEO analysis engine with streaming support
│   ├── search_analysis.py  # 🔍 Search analysis and ranking functions
│   ├── openai.py          # 🤖 OpenAI Responses API integration with web search
│   └── utils.py           # 🛠️ Brand analysis and utility functions
├── prompts/               # 📝 AI prompt templates
│   ├── brandDescription.txt    # Prompt for brand description extraction
│   ├── brandIndustry.txt      # Prompt for industry classification
│   ├── brandCompetitors.txt   # Prompt for competitor identification
│   ├── brandName.txt          # Prompt for brand name extraction
│   ├── brandPromptsGeneration.txt  # Prompt for query generation
│   └── translateString.txt    # Prompt for translation services
├── templates/             # 🎨 Web interface templates
│   └── index.html         # Interactive web interface with streaming support
├── utils/                 # 📊 Configuration and mapping files
│   └── countryLanguage.json   # Country-language mappings for localization
├── notebooks/             # 📓 Analysis notebooks
│   └── openAI.ipynb       # Example Jupyter notebook with GEO analysis
├── server.py              # 🖥️ Flask web server with streaming endpoints
├── requirements.txt       # 📦 Python dependencies
├── CLAUDE.md             # 🤖 AI development guidelines
├── LICENSE               # ⚖️ License information
├── .env.example          # 🔧 Environment variables template
└── README.md             # 📚 This documentation
```

## Configuration

The application uses the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `PROJECT_DIRECTORY`: Absolute path to the project directory (required)

### Understanding GEO vs SEO

**Traditional SEO** focuses on optimizing for search engine rankings (Google, Bing, etc.)
**GEO (Generative Engine Optimization)** focuses on optimizing for AI assistant responses (ChatGPT, Claude, etc.)

This tool helps you understand and improve your **GEO performance** - how your brand appears when users ask AI assistants for recommendations, comparisons, or information.

## 📦 Dependencies

- `openai>=1.0.0` - OpenAI API client for LLM interactions
- `langchain>=0.1.0` - LangChain framework for prompt templates and AI workflows
- `python-dotenv>=1.0.0` - Environment variable management and configuration
- `flask>=2.0.0` - Web framework with streaming support
- `requests>=2.25.0` - HTTP client for external API integrations
- `beautifulsoup4>=4.9.0` - HTML parsing for web scraping capabilities
- `pocketflow` - Workflow management for complex analysis pipelines

## 🎯 What Makes Evidentia Unique

### Advanced GEO Capabilities
- **First-of-its-kind streaming GEO analysis** with real-time progress tracking
- **Multi-model testing framework** supporting various LLM providers
- **Intelligent query generation** tailored to specific industries and markets
- **Comprehensive brand positioning analysis** with sentiment scoring

### Real-Time User Experience
- **Live streaming updates** during analysis with detailed progress indicators
- **Interactive web interface** with modern UI/UX design
- **Color-coded logging system** for easy monitoring of analysis steps
- **Responsive design** that works across all devices

### Enterprise-Ready Features
- **Scalable architecture** supporting multiple concurrent analyses
- **Comprehensive API** with both streaming and traditional endpoints
- **Detailed reporting** with actionable insights and optimization suggestions
- **Geographic market analysis** with country-specific insights

## Development

To run in development mode:

```bash
source venv/bin/activate
export FLASK_DEBUG=1
python server.py
```

The server will automatically reload when you make changes to the code.

## 📊 API Response Examples

### Streaming Brand Analysis Response
```json
{
  "status": "Analysis complete!",
  "step": "complete",
  "result": {
    "name": "Jethr",
    "description": "A technology company specializing in AI-powered solutions...",
    "industry": "Technology",
    "competitors": {
      "direct_competitors": ["Competitor1", "Competitor2"],
      "indirect_competitors": ["Alternative1", "Alternative2"]
    }
  }
}
```

### GEO Analysis Response
```json
{
  "status": "GEO Analysis complete!",
  "step": "complete",
  "progress": 100,
  "result": {
    "brand_name": "YourBrand",
    "total_queries_tested": 10,
    "llm_models_tested": ["gpt-4o-mini-2024-07-18", "gpt-3.5-turbo"],
    "overall_metrics": {
      "mention_rate": 75.5,
      "positive_positioning": 85.2,
      "neutral_positioning": 12.3,
      "negative_positioning": 2.5,
      "average_mention_position": 1.8,
      "brand_visibility_score": 82.4
    },
    "model_performance": {
      "gpt-4o-mini-2024-07-18": {
        "mention_rate": 80.0,
        "average_position": 1.5,
        "sentiment_distribution": {
          "positive": 90.0,
          "neutral": 10.0,
          "negative": 0.0
        }
      }
    },
    "query_performance": [
      {
        "query": "What are the best tech companies?",
        "model": "gpt-4o-mini-2024-07-18",
        "brand_mentioned": true,
        "mention_position": 1,
        "sentiment": "positive",
        "context": "recommendation",
        "competitors_mentioned": [],
        "llm_response": "YourBrand is a leading technology company..."
      }
    ],
    "competitor_analysis": {
      "Competitor1": {
        "mentions": 3,
        "average_position": 2.5
      }
    },
    "optimization_suggestions": [
      "🔍 Low mention rate detected. Consider creating more content...",
      "😊 Improve positive sentiment by highlighting customer success stories..."
    ]
  }
}
```

### Available Models Response
```json
{
  "models": [
    "gpt-4o-mini-2024-07-18",
    "gpt-3.5-turbo",
    "gpt-4-turbo"
  ]
}
```

### Web Search Analysis Response
```json
{
  "summary": "Latest AI automation trends show increased adoption of conversational AI, workflow automation platforms, and no-code solutions for small businesses.",
  "key_insights": [
    "70% increase in small business AI tool adoption in 2024",
    "Conversational AI and chatbots leading market growth",
    "No-code automation platforms becoming dominant"
  ],
  "sources": [
    {
      "title": "AI Automation Trends 2024 Report",
      "url": "https://example.com/ai-trends-2024",
      "snippet": "Small businesses are rapidly adopting AI automation tools..."
    },
    {
      "title": "Market Research: Business Automation Growth",
      "url": "https://example.com/automation-market",
      "snippet": "The automation market is expected to reach $35B by 2025..."
    }
  ],
  "search_quality": "high",
  "last_updated": "recent",
  "web_search_annotations": {
    "msg_001": [
      {
        "type": "web_search",
        "search_query": "AI automation trends 2024 small business",
        "results_count": 15
      }
    ]
  }
}
```

### Formatted Query Analysis Report

Here's how to format detailed query analysis results for better readability:

```markdown
# 📊 Detailed Query Analysis Report

## Query Performance Summary
- **Total Queries Tested**: 2
- **LLM Model**: gpt-4o-mini-2024-07-18
- **Brand**: Jethr
- **Overall Performance**: ❌ No mentions detected

---

## 🔍 Individual Query Results

### Query #1: Workflow Automation Discovery
**Topic**: Discover workflow automation tools  
**Prompt**: "Find me a software tool that automates workflow processes for small businesses in Italy."

| Metric | Result |
|--------|--------|
| **Status** | ❌ Not Mentioned |
| **Sentiment** | 😐 Neutral |
| **Brand Context** | No mention of Jethr in the response |

**LLM Response Preview**:
> "Here are some software tools that can help automate workflow processes for small businesses in Italy: 1. **Zapier**: This tool allows you to connect..."

**Analysis**: The response focused on established automation platforms like Zapier, without mentioning Jethr. This indicates low brand awareness in the workflow automation space.

---

### Query #2: Implementation Strategy Guide
**Topic**: Step-by-step implementation plan  
**Prompt**: "Create a step-by-step guide for implementing a business automation strategy in a local Italian company."

| Metric | Result |
|--------|--------|
| **Status** | ❌ Not Mentioned |
| **Sentiment** | 😐 Neutral |
| **Brand Context** | No mention of the brand Jethr |

**LLM Response Preview**:
> "### Step-by-Step Implementation Plan for a Business Automation Strategy in a Local Italian Company Implementing a business automation strategy can st..."

**Analysis**: The response provided generic implementation guidance without referencing Jethr as a potential solution provider.

---

## 📈 Optimization Recommendations

1. **🎯 Increase Content Marketing**: Create more content around workflow automation for Italian SMBs
2. **🔍 SEO & GEO Strategy**: Optimize for queries about "Italian business automation" and "workflow tools Italy"
3. **📝 Case Studies**: Develop Italian customer success stories and implementation guides
4. **🤝 Partnerships**: Consider partnerships with Italian business organizations
5. **🌍 Local Presence**: Strengthen Italian market presence and localization
```

## Troubleshooting

1. **"No module named 'libs'"** - Make sure `PROJECT_DIRECTORY` is set correctly in `.env`
2. **OpenAI API errors** - Verify your API key is valid and has sufficient credits
3. **Permission errors** - Ensure the virtual environment is activated
4. **Port already in use** - The server runs on port 5000 by default

## License

[Add your license information here]