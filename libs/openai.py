import sys
import os

import json
from langchain.prompts import PromptTemplate
from openai import OpenAI
import libs.utils as utils
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
    Generates a set of coherent queries related to a brand using an LLM (OpenAI) and a prompt template.

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
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    llmClient = OpenAI(api_key=api_key)

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

    # # Get the target language for the brand's country, defaulting to English
    # targetLanguage = countryLanguages.get(brandCountry.lower(), 'english').lower()

    # # Translate the prompt if the target language is not English and translation is successful
    # if targetLanguage != 'english':
    #     translatedPrompt = utils.translateString(prompt, targetLanguage)
    #     if 'NULL' not in translatedPrompt:
    #         prompt = translatedPrompt

    # Call the OpenAI API to generate the queries
    response = llmClient.responses.create(
        model="gpt-4o-mini-2024-07-18",
        tools=[{"type": "web_search_preview"}],
        input=prompt,
    )
    # Extract the competitors from the response
    messagesAnnotations, messagesTexts = getResponseInfo(response)
    rawJson = next(iter(messagesTexts.values()), "")

    # Remove code block markers if present
    if rawJson.startswith("```json"):
        rawJson = rawJson[len("```json"):].strip()
    
    if rawJson.endswith("```"):
        rawJson = rawJson[:-3].strip()

    if not rawJson.strip():
        raise ValueError("No JSON output received from OpenAI API.")

    # Parse and return the JSON as a Python dictionary
    return json.loads(rawJson)