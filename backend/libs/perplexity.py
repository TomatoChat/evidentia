import os
import json
import requests
from langchain.prompts import PromptTemplate
import logging

# Get the absolute path to the backend directory
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(backend_dir, 'utils/countryLanguage.json'), 'r', encoding='utf-8') as file:
    countryLanguages = json.load(file)


class PerplexityClient:
    """
    Client for interacting with Perplexity AI API.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Perplexity client.
        
        Args:
            api_key (str, optional): Perplexity API key. If not provided, 
                                   will look for PERPLEXITY_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable is not set or api_key not provided")
        
        self.base_url = "https://api.perplexity.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(self, messages: list, model: str = "llama-3.1-sonar-large-128k-online", **kwargs):
        """
        Create a chat completion using Perplexity AI.
        
        Args:
            messages (list): List of message objects
            model (str): Model to use for completion
            **kwargs: Additional parameters like temperature, max_tokens, etc.
        
        Returns:
            dict: Response from Perplexity API
        """
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        return response.json()


def getResponseInfo(response: dict) -> tuple[dict, str]:
    """
    Extracts text information from a Perplexity AI chat completion response.

    Args:
        response (dict): The response object returned by Perplexity's chat completion API.

    Returns:
        tuple:
            - citations (dict): A dictionary containing citation information.
            - message_text (str): The main response text content.
    """
    try:
        message_text = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        citations = response.get("citations", [])
        
        return {"citations": citations}, message_text
    except (KeyError, IndexError) as e:
        logging.error(f"Error extracting response info: {e}")
        return {}, ""


def getCoherentQueries(brandName: str, brandCountry: str, brandDescription: str, brandIndustry: str, totalQueries: int = 100):
    """
    Generates a set of coherent queries related to a brand using Perplexity AI with web search capabilities.

    Args:
        brandName (str): The name of the brand/company.
        brandCountry (str): The country where the brand/company is based.
        brandDescription (str): A description of the brand/company.
        brandIndustry (str): The industry in which the brand/company operates.
        totalQueries (int, optional): The total number of queries to generate. Defaults to 100.

    Returns:
        list: A list of dictionaries containing the generated queries, parsed from the JSON response.
    """
    # Initialize the Perplexity client
    client = PerplexityClient()

    try:
        # Load the prompt template for generating queries from file
        project_dir = os.path.dirname(backend_dir)
        with open(os.path.join(project_dir, "prompts/brandPromptsGeneration.txt"), "r", encoding="utf-8") as file:
            promptTemplate = file.read()

        # Format the prompt with the provided brand information and total queries
        prompt = PromptTemplate(
            input_variables=["companyName", "companyCountry", "companyDescription", "companyIndustry", "totalQueries"],
            template=promptTemplate
        ).format(
            companyName=brandName,
            companyCountry=brandCountry,
            companyDescription=brandDescription,
            companyIndustry=brandIndustry,
            totalQueries=totalQueries
        )

        # Prepare messages for Perplexity API
        messages = [
            {
                "role": "system",
                "content": "You are a brand analysis expert. Generate coherent search queries that would help analyze a brand's online presence and competitive landscape. Always respond with valid JSON format."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]

        # Call the Perplexity API with online search capabilities
        response = client.chat_completion(
            messages=messages,
            model="llama-3.1-sonar-large-128k-online",
            temperature=0.7,
            max_tokens=4000
        )
        
        # Extract response information
        citations, rawJson = getResponseInfo(response)

        # Clean up JSON formatting
        if rawJson.startswith("```json"):
            rawJson = rawJson[len("```json"):].strip()
        if rawJson.endswith("```"):
            rawJson = rawJson[:-3].strip()

        if not rawJson.strip():
            raise ValueError("No JSON output received from Perplexity API.")

        # Parse and return the JSON as a Python dictionary
        queries_result = json.loads(rawJson)
        
        # Log citations if available for debugging
        if citations.get("citations"):
            logging.info(f"Perplexity search citations available for query generation: {len(citations['citations'])} sources")
        
        return queries_result
        
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON from Perplexity query generation response: {e}")
        raise ValueError(f"Invalid JSON response from Perplexity API: {e}")
    except FileNotFoundError:
        logging.error("Brand prompt template file not found")
        raise ValueError("Brand prompt template file 'prompts/brandPromptsGeneration.txt' not found")
    except Exception as e:
        logging.error(f"Perplexity query generation failed: {e}")
        raise ValueError(f"Failed to generate queries using Perplexity: {e}")


def webSearchAndAnalyze(query: str, context: str = "") -> dict:
    """
    Performs web search using Perplexity AI and analyzes the results.
    
    Args:
        query (str): The search query to execute
        context (str, optional): Additional context for the analysis
    
    Returns:
        dict: Contains search results, analysis, and citations
    """
    # Initialize the Perplexity client
    client = PerplexityClient()
    
    # Construct the prompt for web search and analysis
    system_prompt = """You are an expert research analyst. Search the web for comprehensive information and provide detailed analysis. Always format your response as valid JSON."""
    
    user_prompt = f"""
    Please search the web for information about: {query}
    
    {f"Additional context: {context}" if context else ""}
    
    After searching, please provide:
    1. A summary of the key findings
    2. The most relevant sources and insights
    3. Any important trends or patterns identified
    
    Format your response as JSON with the following structure:
    {{
        "summary": "Brief summary of findings",
        "key_insights": ["insight 1", "insight 2", "insight 3"],
        "sources": [
            {{"title": "Source title", "url": "https://example.com", "snippet": "relevant excerpt"}},
            {{"title": "Source title 2", "url": "https://example2.com", "snippet": "relevant excerpt"}}
        ],
        "search_quality": "high/medium/low",
        "last_updated": "recent/moderate/outdated"
    }}
    """
    
    try:
        # Prepare messages for Perplexity API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Call the Perplexity API with online search capabilities
        response = client.chat_completion(
            messages=messages,
            model="llama-3.1-sonar-large-128k-online",
            temperature=0.3,
            max_tokens=4000
        )
        
        # Extract response information including citations
        citations, rawJson = getResponseInfo(response)
        
        # Clean up JSON formatting
        if rawJson.startswith("```json"):
            rawJson = rawJson[len("```json"):].strip()
        if rawJson.endswith("```"):
            rawJson = rawJson[:-3].strip()
            
        if not rawJson.strip():
            raise ValueError("No JSON output received from Perplexity web search.")
        
        # Parse the JSON response
        analysis_result = json.loads(rawJson)
        
        # Add Perplexity citations to the result
        analysis_result["perplexity_citations"] = citations
        analysis_result["model_used"] = "llama-3.1-sonar-large-128k-online"
        
        return analysis_result
        
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON from Perplexity web search response: {e}")
        return {
            "error": "Failed to parse search results",
            "raw_response": rawJson,
            "summary": "Search completed but response format was invalid",
            "key_insights": [],
            "sources": [],
            "search_quality": "low",
            "last_updated": "unknown"
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Perplexity API request failed: {e}")
        return {
            "error": f"API request failed: {str(e)}",
            "summary": "Unable to complete search due to API error",
            "key_insights": [],
            "sources": [],
            "search_quality": "low",
            "last_updated": "unknown"
        }
    except Exception as e:
        logging.error(f"Perplexity web search failed: {e}")
        return {
            "error": f"Search failed: {str(e)}",
            "summary": "Search encountered an unexpected error",
            "key_insights": [],
            "sources": [],
            "search_quality": "low",
            "last_updated": "unknown"
        }


def getBrandAnalysis(brandName: str, brandWebsite: str, competitors: list = None) -> dict:
    """
    Performs comprehensive brand analysis using Perplexity AI's web search capabilities.
    
    Args:
        brandName (str): The brand name to analyze
        brandWebsite (str): The brand's website URL
        competitors (list, optional): List of competitor names
    
    Returns:
        dict: Comprehensive brand analysis including market position, sentiment, etc.
    """
    client = PerplexityClient()
    
    competitors_text = f"Compare with competitors: {', '.join(competitors)}" if competitors else ""
    
    prompt = f"""
    Analyze the brand "{brandName}" (website: {brandWebsite}) comprehensively.
    {competitors_text}
    
    Please provide a detailed analysis including:
    1. Brand reputation and sentiment analysis
    2. Market position and competitive landscape
    3. Recent news and developments
    4. Customer reviews and feedback trends
    5. Digital presence and social media activity
    
    Format as JSON:
    {{
        "brand_name": "{brandName}",
        "overall_sentiment": "positive/neutral/negative",
        "market_position": "description of market position",
        "reputation_score": "1-10 scale",
        "recent_developments": ["development 1", "development 2"],
        "competitive_analysis": {{
            "strengths": ["strength 1", "strength 2"],
            "weaknesses": ["weakness 1", "weakness 2"],
            "opportunities": ["opportunity 1", "opportunity 2"],
            "threats": ["threat 1", "threat 2"]
        }},
        "digital_presence": {{
            "website_quality": "high/medium/low",
            "social_media_activity": "active/moderate/inactive",
            "content_strategy": "description"
        }}
    }}
    """
    
    try:
        messages = [
            {"role": "system", "content": "You are a brand analysis expert with access to real-time web information. Provide comprehensive, accurate analysis based on current data."},
            {"role": "user", "content": prompt}
        ]
        
        response = client.chat_completion(
            messages=messages,
            model="llama-3.1-sonar-large-128k-online",
            temperature=0.2,
            max_tokens=5000
        )
        
        citations, rawJson = getResponseInfo(response)
        
        # Clean up JSON formatting
        if rawJson.startswith("```json"):
            rawJson = rawJson[len("```json"):].strip()
        if rawJson.endswith("```"):
            rawJson = rawJson[:-3].strip()
        
        analysis_result = json.loads(rawJson)
        analysis_result["perplexity_citations"] = citations
        analysis_result["analysis_timestamp"] = "current"
        
        return analysis_result
        
    except Exception as e:
        logging.error(f"Brand analysis failed: {e}")
        return {
            "error": f"Analysis failed: {str(e)}",
            "brand_name": brandName,
            "overall_sentiment": "unknown",
            "market_position": "Unable to determine",
            "reputation_score": "N/A"
        } 