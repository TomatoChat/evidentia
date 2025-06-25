# Evidentia - Brand Research Tool

A powerful brand research tool that uses OpenAI to analyze companies and generate relevant search queries for market research purposes.

## Features

- **Company Analysis**: Automatically extract company descriptions, industries, and competitors
- **Query Generation**: Generate targeted search queries for market research
- **Multi-language Support**: Supports 50+ countries with localized language processing
- **Web Interface**: Simple, intuitive web interface for easy interaction
- **API Endpoints**: RESTful API for programmatic access

## Quick Start

### Prerequisites

- Python 3.7+
- OpenAI API key
- Required Python packages (see Installation)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd evidentia
```

2. Install required packages:
```bash
pip install flask python-dotenv openai langchain
```

3. Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
PROJECT_DIRECTORY=/path/to/evidentia
```

### Running the Application

#### Web Interface (Recommended)

1. Start the Flask server:
```bash
python server.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Fill out the form with:
   - **Brand Name**: The company you want to analyze
   - **Brand Website**: Company website (e.g., example.com)
   - **Brand Country**: Select from 50+ supported countries
   - **Number of Queries**: How many search queries to generate (1-50)

4. Click "Analyze Brand" and wait for results

#### Jupyter Notebook

1. Open the notebook:
```bash
jupyter notebook notebooks/openAI.ipynb
```

2. Update the variables in the second cell:
```python
brandName = "your_brand_name"
brandWebsite = "your_brand_website.com"
brandCountry = "your_country"
```

3. Run all cells to see the analysis

#### Python Script

```python
import libs.utils as utils
import libs.openai as openaiAnalytics

# Get company information
brand_info = utils.getCompanyInfo("BrandName", "website.com", "italy")

# Generate search queries
queries = openaiAnalytics.getCoherentQueries(
    brand_info['name'], 
    "italy", 
    brand_info['description'], 
    brand_info['industry'], 
    10
)

print("Brand Info:", brand_info)
print("Queries:", queries)
```

## API Endpoints

### GET /
Returns the web interface HTML page.

### POST /analyze
Analyzes a brand and generates search queries.

**Request Body:**
```json
{
  "brandName": "Example Corp",
  "brandWebsite": "example.com",
  "brandCountry": "italy",
  "totalQueries": 10
}
```

**Response:**
```json
{
  "brandInfo": {
    "name": "Example Corp",
    "description": "Company description...",
    "industry": "Technology",
    "competitors": [
      {
        "name": "Competitor 1",
        "description": "Competitor description..."
      }
    ]
  },
  "queries": [
    {
      "topic": "Find CRM tools",
      "prompt": "Recommend a CRM system for small businesses..."
    }
  ]
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Project Structure

```
evidentia/
├── libs/
│   ├── openai.py          # OpenAI API integration
│   └── utils.py           # Utility functions
├── notebooks/
│   └── openAI.ipynb       # Jupyter notebook example
├── prompts/
│   ├── brandCompetitors.txt
│   ├── brandDescription.txt
│   ├── brandIndustry.txt
│   ├── brandName.txt
│   ├── brandPromptsGeneration.txt
│   └── translateString.txt
├── utils/
│   └── countryLanguage.json
├── server.py              # Flask web server
├── .env                   # Environment variables
└── README.md
```

## Supported Countries

The tool supports 50+ countries with localized language processing:

- **Europe**: Italy, France, Germany, Spain, UK, etc.
- **Americas**: USA, Canada, Brazil, Argentina, etc.
- **Asia**: China, Japan, India, South Korea, etc.
- **Africa**: South Africa, Nigeria, Kenya, etc.
- **Oceania**: Australia, New Zealand

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
PROJECT_DIRECTORY=/full/path/to/evidentia

# Optional
FLASK_ENV=development
FLASK_DEBUG=True
```

## Troubleshooting

### Common Issues

1. **"No module named 'libs'"**
   - Ensure `PROJECT_DIRECTORY` in `.env` points to the correct path
   - Verify you're running from the project root directory

2. **OpenAI API errors**
   - Check your API key is valid and has sufficient credits
   - Ensure `OPENAI_API_KEY` is set in `.env`

3. **Translation issues**
   - Some countries may not have full translation support
   - Queries will default to English if translation fails

### Logging

Enable debug logging by setting:
```bash
FLASK_DEBUG=True
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions, please open an issue on the GitHub repository.