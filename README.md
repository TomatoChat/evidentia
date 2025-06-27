# Evidentia - Generative Engine Optimization (GEO) Tool

🤖 A powerful GEO analysis tool that helps brands understand their positioning in LLM responses and optimize for generative AI engines.

## What is GEO?

**Generative Engine Optimization (GEO)** is the practice of optimizing content and brand positioning for Large Language Models (LLMs) and AI-powered responses, rather than traditional search engines. As users increasingly rely on AI assistants for recommendations and information, GEO becomes crucial for brand visibility.

## Features

- **LLM Brand Analysis**: Analyze how your brand appears in AI responses across different models
- **Query Generation**: Creates test queries to evaluate brand positioning
- **Multi-Model Testing**: Test across GPT-4, GPT-3.5, and other LLM models
- **Sentiment Analysis**: Understand how AI portrays your brand (positive/neutral/negative)
- **Competitor Comparison**: See how competitors are positioned in AI responses
- **Optimization Suggestions**: Get actionable GEO improvement recommendations
- **Real-time Streaming**: Watch analysis progress in real-time

## Prerequisites

- Python 3.11 or higher
- OpenAI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd evidentia
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   PROJECT_DIRECTORY=/path/to/your/evidentia/directory
   
   # Optional - for real Google search results (100 free searches/month)
   SERPAPI_KEY=your_serpapi_key_here
   ```

## Usage

### Web Interface

1. **Start the server**
   ```bash
   source venv/bin/activate
   python server.py
   ```

2. **Open your browser**
   Navigate to `http://127.0.0.1:5000`

3. **Use the GEO analysis**
   - Enter brand name (e.g., "jethr")
   - Enter brand website (e.g., "jethr.com")
   - Optionally specify country (defaults to "world")
   - Click "Analyze Brand" to get company information
   - Click "Generate Queries" to create LLM test queries
   - Click "Test Queries & Rankings" to analyze brand positioning in AI responses

### API Endpoints

#### Brand Information
```bash
POST /brand-info
Content-Type: application/json

{
  "brandName": "jethr",
  "brandWebsite": "jethr.com",
  "brandCountry": "italy"
}
```

#### Generate LLM Test Queries
```bash
POST /generate-queries
Content-Type: application/json

{
  "brandName": "Company Name",
  "brandCountry": "italy",
  "brandDescription": "Company description...",
  "brandIndustry": "Technology",
  "totalQueries": 10
}
```

#### GEO Analysis (LLM Brand Positioning)
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

#### Health Check
```bash
GET /health
```

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
```

## Project Structure

```
evidentia/
├── libs/
│   ├── openai.py          # OpenAI integration functions
│   └── utils.py           # Utility functions for brand analysis
├── prompts/
│   ├── brandDescription.txt    # Prompt for brand description
│   ├── brandIndustry.txt      # Prompt for industry analysis
│   ├── brandCompetitors.txt   # Prompt for competitor analysis
│   ├── brandName.txt          # Prompt for brand name extraction
│   ├── brandPromptsGeneration.txt  # Prompt for query generation
│   └── translateString.txt    # Prompt for translation
├── templates/
│   └── index.html         # Web interface template
├── utils/
│   └── countryLanguage.json   # Country-language mappings
├── notebooks/
│   └── openAI.ipynb       # Example Jupyter notebook
├── server.py              # Flask web server
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Configuration

The application uses the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `PROJECT_DIRECTORY`: Absolute path to the project directory (required)

### Understanding GEO vs SEO

**Traditional SEO** focuses on optimizing for search engine rankings (Google, Bing, etc.)
**GEO (Generative Engine Optimization)** focuses on optimizing for AI assistant responses (ChatGPT, Claude, etc.)

This tool helps you understand and improve your **GEO performance** - how your brand appears when users ask AI assistants for recommendations, comparisons, or information.

## Dependencies

- `openai>=1.0.0` - OpenAI API client
- `langchain>=0.1.0` - LangChain for prompt templates
- `python-dotenv>=1.0.0` - Environment variable management
- `flask>=2.0.0` - Web framework
- `pocketflow` - Additional utilities for data flow

## Development

To run in development mode:

```bash
source venv/bin/activate
export FLASK_DEBUG=1
python server.py
```

The server will automatically reload when you make changes to the code.

## API Response Examples

### Brand Information Response
```json
{
  "name": "Jethr",
  "description": "A technology company specializing in...",
  "industry": "Technology",
  "competitors": {
    "direct_competitors": [...],
    "indirect_competitors": [...]
  }
}
```

### Queries Response
```json
{
  "queries": [
    {
      "query": "search query 1",
      "intent": "brand awareness"
    },
    {
      "query": "search query 2",
      "intent": "competitor analysis"
    }
  ]
}
```

## Troubleshooting

1. **"No module named 'libs'"** - Make sure `PROJECT_DIRECTORY` is set correctly in `.env`
2. **OpenAI API errors** - Verify your API key is valid and has sufficient credits
3. **Permission errors** - Ensure the virtual environment is activated
4. **Port already in use** - The server runs on port 5000 by default

## License

[Add your license information here]