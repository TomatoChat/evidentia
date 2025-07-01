import os
import json
from langchain.prompts import PromptTemplate
from openai import OpenAI
import logging


with open('utils/countryLanguage.json', 'r', encoding='utf-8') as file:
    countryLanguages = json.load(file)


def getResponseInfo(response) -> tuple[dict, dict]:
    """
    Extracts annotation and text information from an OpenAI responses.create API call.

    This function processes the response object returned by OpenAI"s responses.create endpoint.
    It filters for outputs of type "message", then extracts the "output_text" content, 
    collecting both the text and any associated annotations for each message.

    Args:
        response (OpenAI.responses.response.Response): 
            The response object returned by OpenAI's responses.create API call.

    Returns:
        tuple:
            - messagesAnnotations (dict): 
                A dictionary mapping each message ID to its list of annotations.
            - messagesTexts (dict): 
                A dictionary mapping each message ID to its output text.
    """
    response = response.to_dict()
    outputMessages = [output for output in response["output"] if output.get("type") == "message"]
    messageTextContents = {message["id"]: content for message in outputMessages for content in message.get("content", []) if content.get("type") == "output_text"}
    messagesAnnotations = {messageId: textContent["annotations"] for messageId, textContent in messageTextContents.items()}
    messagesTexts = {messageId: textContent["text"] for messageId, textContent in messageTextContents.items()}

    return messagesAnnotations, messagesTexts


def getCoherentQueries(brandName: str, brandCountry: str, brandDescription: str, brandIndustry: str, totalQueries: int = 100):
    """
    Generates a set of coherent queries related to a brand using an LLM (OpenAI) with web search capabilities.

    Args:
        brandName (str): The name of the brand/company.
        brandCountry (str): The country where the brand/company is based.
        brandDescription (str): A description of the brand/company.
        brandIndustry (str): The industry in which the brand/company operates.
        totalQueries (int, optional): The total number of queries to generate. Defaults to 100.

    Returns:
        list: A list of dictionaries containing the generated queries, parsed from the JSON response.
    """
    # Initialize the OpenAI client
    apiKey = os.getenv("OPENAI_API_KEY")

    if not apiKey:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    llmClient = OpenAI(api_key=apiKey)

    try:
        # Load the prompt template for generating queries from file
        with open("prompts/brandPromptsGeneration.txt", "r", encoding="utf-8") as file:
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

        # Call the OpenAI Responses API with web search enabled for better query generation
        response = llmClient.responses.create(
            model="gpt-4o-mini-2024-07-18",
            tools=[{"type": "web_search_preview"}],
            input=prompt,
        )
        
        # Extract response information
        messagesAnnotations, messagesTexts = getResponseInfo(response)
        rawJson = next(iter(messagesTexts.values()), "")

        # Clean up JSON formatting
        if rawJson.startswith("```json"):
            rawJson = rawJson[len("```json"):].strip()
        
        if rawJson.endswith("```"):
            rawJson = rawJson[:-3].strip()

        if not rawJson.strip():
            raise ValueError("No JSON output received from OpenAI API.")

        # Parse and return the JSON as a Python dictionary
        queriesResult = json.loads(rawJson)
        
        # Log web search annotations if available for debugging
        if messagesAnnotations:
            logging.info(f"Web search annotations available for query generation: {len(messagesAnnotations)} messages")
        
        return queriesResult
        
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON from query generation response: {e}")
        raise ValueError(f"Invalid JSON response from OpenAI API: {e}")

    except FileNotFoundError:
        logging.error("Brand prompt template file not found")
        raise ValueError("Brand prompt template file 'prompts/brandPromptsGeneration.txt' not found")
    
    except Exception as e:
        logging.error(f"Query generation failed: {e}")
        raise ValueError(f"Failed to generate queries: {e}")
    

def runBulkQueries(queries:list[dict], llmModel:str="gpt-4o-mini-2024-07-18"):
    """
    Runs a bulk of queries using an LLM (OpenAI) with web search capabilities.

    Args:
        queries (list[dict]): A list of dictionaries containing the queries to run.
        llmModel (str, optional): The model to use for the queries. Defaults to "gpt-4o-mini-2024-07-18".
    """

    apiKey = os.getenv("OPENAI_API_KEY")

    if not apiKey:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    llmClient = OpenAI(api_key=apiKey)
    results = []
    
    for query in queries:
        response = llmClient.responses.create(
            model=llmModel,
            tools=[{"type": "web_search_preview"}],
            input=query["prompt"],
        )
        
        messagesAnnotations, messagesTexts = getResponseInfo(response)
        rawJson = next(iter(messagesTexts.values()), "")

        results.append({
            "query": query,
            "messageAnnotations": messagesAnnotations,
            "messageTexts": messagesTexts
        })
        
    return results