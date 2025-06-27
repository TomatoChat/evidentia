# Evidentia - Brand Research Tool

🔍 A powerful brand research tool that analyzes companies and generates coherent search queries for brand intelligence gathering.

## Features

- **Brand Analysis**: Automatically extracts company description, industry, and competitors
- **Query Generation**: Creates coherent search queries based on brand information
- **Web Interface**: User-friendly form for easy brand analysis
- **REST API**: Programmatic access to all functionality
- **Multi-language Support**: Supports analysis in different languages based on country

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
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   PROJECT_DIRECTORY=/path/to/your/evidentia/directory
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

3. **Use the form**
   - Enter brand name (e.g., "jethr")
   - Enter brand website (e.g., "jethr.com")
   - Optionally specify country (defaults to "world")
   - Click "Analyze Brand" to get company information
   - Click "Generate Queries" to create search queries

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

#### Generate Queries
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

## Dependencies

- `openai>=1.0.0` - OpenAI API client
- `langchain>=0.1.0` - LangChain for prompt templates
- `python-dotenv>=1.0.0` - Environment variable management
- `flask>=2.0.0` - Web framework

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