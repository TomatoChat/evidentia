import sys
import os
from dotenv import load_dotenv
load_dotenv()
os.chdir(os.getenv("PROJECT_DIRECTORY"))
sys.path.append(os.getenv("PROJECT_DIRECTORY"))

from langchain.prompts import PromptTemplate
from openai import OpenAI
import libs.openai as openaiAnalytics
import json


with open('utils/countryLanguage.json', 'r', encoding='utf-8') as file:
    countryLanguages = json.load(file)


def translateString(stringToTranslate: str, targetLanguage: str) -> str:
    """
    Translates a given string into the specified target language using an LLM (OpenAI) and a prompt template.

    Args:
        stringToTranslate (str): The text string to be translated.
        targetLanguage (str): The language to translate the string into.

    Returns:
        str: The translated string, or an empty string if translation fails.
    """
    # Initialize the OpenAI client
    llmClient = OpenAI()

    # Load the translation prompt template from file
    with open("prompts/translateString.txt", "r", encoding="utf-8") as file:
        promptTemplate = file.read()

    # Format the prompt with the string to translate and the target language
    prompt = PromptTemplate(
        input_variables=["stringToTranslate", "targetLanguage"],
        template=promptTemplate
    ).format(
        stringToTranslate=stringToTranslate,
        targetLanguage=targetLanguage
    )

    # Call the OpenAI API to get the translation
    response = llmClient.responses.create(
        model="gpt-4o-mini-2024-07-18",
        input=prompt,
    )
    
    # Extract the translated text from the response
    messagesAnnotations, messagesTexts = openaiAnalytics.getResponseInfo(response)

    # Return the first translated message, or an empty string if none
    return next(iter(messagesTexts.values()), "")


def getBrandDescription(clientOpenai, brandName: str, brandWebsite: str, brandCountry: str = "world") -> str:
    """
    Retrieves the company description using OpenAI's responses API and the brandDescription prompt template.

    Args:
        clientOpenai: An initialized OpenAI client instance.
        brandName (str): The name of the brand/company.
        brandWebsite (str): The website of the brand/company.
        brandCountry (str, optional): The country of the brand/company. Defaults to "world".

    Returns:
        str: The company description, translated if necessary.
    """
    # Load the brand description prompt template from file
    with open("prompts/brandDescription.txt", "r", encoding="utf-8") as file:
        promptTemplate = file.read()

    # Format the prompt with the provided brand information
    prompt = PromptTemplate(
        input_variables=["companyName", "companyWebsite", "companyCountry"],
        template=promptTemplate
    ).format(
        companyName=brandName,
        companyWebsite=brandWebsite,
        companyCountry=brandCountry
    )

    # Determine the target language for the description
    targetLanguage = countryLanguages.get(brandCountry.lower(), 'english').lower()

    # If the target language is not English, translate the prompt
    if targetLanguage != 'english':
        translatedPrompt = translateString(prompt, targetLanguage)

        if 'NULL' not in translatedPrompt:
            prompt = translatedPrompt
    
    # Call the OpenAI API to get the company description
    response = clientOpenai.responses.create(
        model="gpt-4o-mini-2024-07-18",
        tools=[{"type": "web_search_preview"}],
        input=prompt,
    )
    # Extract the description from the response
    messagesAnnotations, messagesTexts = openaiAnalytics.getResponseInfo(response)

    # Return the first description message, or an empty string if none
    return next(iter(messagesTexts.values()), "")


def getBrandIndustry(clientOpenai, brandName: str, brandWebsite: str, brandDescription: str, brandCountry: str = "world") -> str:
    """
    Retrieves the company industry using OpenAI's responses API and the brandIndustry prompt template.

    Args:
        clientOpenai: An initialized OpenAI client instance.
        brandName (str): The name of the brand/company.
        brandWebsite (str): The website of the brand/company.
        brandDescription (str): A description of the brand/company.
        brandCountry (str, optional): The country of the brand/company. Defaults to "world".

    Returns:
        str: The company industry as determined by the LLM, translated if necessary.
    """
    # Load the brand industry prompt template from file
    with open("prompts/brandIndustry.txt", "r", encoding="utf-8") as file:
        promptTemplate = file.read()

    # Format the prompt with the provided brand information
    prompt = PromptTemplate(
        input_variables=["companyName", "companyWebsite", "companyCountry", "companyDescription"],
        template=promptTemplate
    ).format(
        companyName=brandName,
        companyWebsite=brandWebsite,
        companyCountry=brandCountry,
        companyDescription=brandDescription
    )

    # Get the target language for the brand's country, defaulting to English
    targetLanguage = countryLanguages.get(brandCountry.lower(), 'english').lower()

    # Translate the prompt if the target language is not English and translation is successful
    if targetLanguage != 'english':
        translatedPrompt = translateString(prompt, targetLanguage)

        if 'NULL' not in translatedPrompt:
            prompt = translatedPrompt

    # Call the OpenAI API to get the company industry
    response = clientOpenai.responses.create(
        model="gpt-4o-mini-2024-07-18",
        tools=[{"type": "web_search_preview"}],
        input=prompt,
    )
    # Extract the industry from the response
    messagesAnnotations, messagesTexts = openaiAnalytics.getResponseInfo(response)

    # Return the first industry message, or an empty string if none
    return next(iter(messagesTexts.values()), "")


def getBrandCompetitors(clientOpenai, brandName: str, brandWebsite: str, brandDescription: str, brandIndustry: str, brandCountry: str = "world") -> dict:
    """
    Retrieves the company's competitors using OpenAI's responses API and the brandCompetitors prompt template.

    Args:
        clientOpenai: An initialized OpenAI client instance.
        brandName (str): The name of the brand/company.
        brandWebsite (str): The website of the brand/company.
        brandDescription (str): A description of the brand/company.
        brandIndustry (str): The industry in which the brand/company operates.
        brandCountry (str, optional): The country of the brand/company. Defaults to "world".

    Returns:
        dict: A dictionary containing the competitors, parsed from the JSON response.
    """
    # Load the brand competitors prompt template from file
    with open("prompts/brandCompetitors.txt", "r", encoding="utf-8") as file:
        promptTemplate = file.read()

    # Format the prompt with the provided brand information
    prompt = PromptTemplate(
        input_variables=["companyName", "companyWebsite", "companyCountry", "companyDescription", "companyIndustry"],
        template=promptTemplate
    ).format(
        companyName=brandName,
        companyWebsite=brandWebsite,
        companyCountry=brandCountry,
        companyDescription=brandDescription,
        companyIndustry=brandIndustry
    )

    # Get the target language for the brand's country, defaulting to English
    targetLanguage = countryLanguages.get(brandCountry.lower(), 'english').lower()

    # Translate the prompt if the target language is not English and translation is successful
    if targetLanguage != 'english':
        translatedPrompt = translateString(prompt, targetLanguage)

        if 'NULL' not in translatedPrompt:
            prompt = translatedPrompt

    # Call the OpenAI API to get the competitors
    response = clientOpenai.responses.create(
        model="gpt-4o-mini-2024-07-18",
        tools=[{"type": "web_search_preview"}],
        input=prompt,
    )
    # Extract the competitors from the response
    messagesAnnotations, messagesTexts = openaiAnalytics.getResponseInfo(response)
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


def getBrandName(clientOpenai, brandDescription: str) -> str:
    """
    Retrieves the company name using OpenAI's responses API and the brandName prompt template.

    Args:
        clientOpenai: An initialized OpenAI client instance.
        brandDescription (str): A description of the brand/company.

    Returns:
        str: The company name as determined by the LLM.
    """
    # Load the brand name prompt template from file
    with open("prompts/brandName.txt", "r", encoding="utf-8") as file:
        promptTemplate = file.read()

    # Format the prompt with the provided brand description
    prompt = PromptTemplate(
        input_variables=["companyDescription"],
        template=promptTemplate
    ).format(
        companyDescription=brandDescription
    )

    # Call the OpenAI API to get the company name
    response = clientOpenai.responses.create(
        model="gpt-4o-mini-2024-07-18",
        tools=[{"type": "web_search_preview"}],
        input=prompt,
    )
    # Extract the name from the response
    messagesAnnotations, messagesTexts = openaiAnalytics.getResponseInfo(response)

    # Return the first name message, or an empty string if none
    return next(iter(messagesTexts.values()), "")


def getCompanyInfo(brandName: str, brandWebsite: str, brandCountry: str = "world") -> dict:
    """
    Retrieves the company description and industry using OpenAI's responses API and prompt templates.

    Args:
        brandName (str): The name of the brand/company.
        brandWebsite (str): The website of the brand/company.
        brandCountry (str, optional): The country of the brand/company. Defaults to "world".

    Returns:
        dict: A dictionary with keys 'description' and 'industry'.
    """
    clientOpenai = OpenAI()
    brandDescription = getBrandDescription(clientOpenai, brandName, brandWebsite, brandCountry)
    brandIndustry = getBrandIndustry(clientOpenai, brandName, brandWebsite, brandCountry, brandDescription)
    brandCompetitors = getBrandCompetitors(clientOpenai, brandName, brandWebsite, brandCountry, brandDescription, brandIndustry)
    brandName = getBrandName(clientOpenai, brandDescription)
    
    return {
        "description": brandDescription,
        "industry": brandIndustry,
        "competitors": brandCompetitors,
        "name": brandName
    }