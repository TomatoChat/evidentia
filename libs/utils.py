import sys
import os

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
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    llmClient = OpenAI(api_key=api_key)

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
    response = llmClient.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7
    )
    
    # Extract the translated text from the response
    return response.choices[0].message.content


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
    
    # Call the OpenAI API to get the company description with structured output
    try:
        response = clientOpenai.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
            timeout=30,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "brand_description",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "A 2-4 sentence business description of the company"
                            }
                        },
                        "required": ["description"],
                        "additionalProperties": False
                    }
                }
            }
        )
        # Extract the description from the structured response
        result = response.choices[0].message.content
        try:
            parsed_result = json.loads(result)
            description = parsed_result.get("description", "")
            if description and description.strip():
                return description
            else:
                # Provide a fallback description
                fallback_description = f"{brandName} is a business operating in {brandCountry} with their website at {brandWebsite}. The company provides digital services and solutions to their customers in the local market."
                return fallback_description
        except json.JSONDecodeError:
            # If structured response fails, try to use the raw content
            if result and result.strip() and result.strip().upper() != "NULL":
                return result
            else:
                # Provide a fallback description
                fallback_description = f"{brandName} is a business operating in {brandCountry} with their website at {brandWebsite}. The company provides digital services and solutions to their customers in the local market."
                return fallback_description
    except Exception as e:
        print(f"Error in getBrandDescription: {e}")
        raise Exception(f"Failed to get brand description: {str(e)}")


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
    try:
        response = clientOpenai.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
            timeout=30
        )
        # Extract the industry from the response
        result = response.choices[0].message.content
        if not result or result.strip() == "":
            raise ValueError("Empty response received from OpenAI API")
        return result
    except Exception as e:
        print(f"Error in getBrandIndustry: {e}")
        raise Exception(f"Failed to get brand industry: {str(e)}")


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

    # Call the OpenAI API to get the competitors with structured output
    try:
        response = clientOpenai.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7,
            timeout=30,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "competitor_analysis",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "competitors": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "description": "The competitor's company name"
                                        },
                                        "website": {
                                            "type": "string",
                                            "description": "The competitor's website URL"
                                        },
                                        "reason": {
                                            "type": "string",
                                            "description": "Brief explanation of why they compete"
                                        }
                                    },
                                    "required": ["name", "website", "reason"],
                                    "additionalProperties": False
                                },
                                "minItems": 3,
                                "maxItems": 5
                            }
                        },
                        "required": ["competitors"],
                        "additionalProperties": False
                    }
                }
            }
        )
        # Extract the competitors from the structured response
        rawJson = response.choices[0].message.content
        
        if not rawJson or not rawJson.strip():
            print("Warning: Empty response from OpenAI API for competitors")
            return {"competitors": []}

        # Parse the structured JSON response
        try:
            result = json.loads(rawJson)
            return result
        except json.JSONDecodeError as json_error:
            print(f"JSON decode error with structured output: {json_error}")
            print(f"Raw response: {rawJson}")
            # Return a fallback structure if parsing fails
            return {"competitors": []}
            
    except Exception as e:
        print(f"Error in getBrandCompetitors: {e}")
        # Return a fallback structure instead of raising an exception
        return {"competitors": []}


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

    # Call the OpenAI API to get the company name with structured output
    try:
        response = clientOpenai.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
            timeout=30,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "brand_name",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The extracted or identified company name"
                            }
                        },
                        "required": ["name"],
                        "additionalProperties": False
                    }
                }
            }
        )
        # Extract the name from the structured response
        result = response.choices[0].message.content
        try:
            parsed_result = json.loads(result)
            name = parsed_result.get("name", "")
            if name and name.strip():
                return name
            else:
                # Extract a reasonable name from the description or use a fallback
                words = brandDescription.split()
                for word in words:
                    if word[0].isupper() and len(word) > 2 and not word.lower() in ['the', 'and', 'for', 'with', 'this', 'that']:
                        return word
                # If no suitable name found, return a generic business name
                return "Business Entity"
        except json.JSONDecodeError:
            # If structured response fails, try to use the raw content
            if result and result.strip() and result.strip().upper() != "NULL":
                return result
            else:
                # Extract a reasonable name from the description or use a fallback
                words = brandDescription.split()
                for word in words:
                    if word[0].isupper() and len(word) > 2 and not word.lower() in ['the', 'and', 'for', 'with', 'this', 'that']:
                        return word
                # If no suitable name found, return a generic business name
                return "Business Entity"
    except Exception as e:
        print(f"Error in getBrandName: {e}")
        raise Exception(f"Failed to get brand name: {str(e)}")


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
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    clientOpenai = OpenAI(api_key=api_key)
    brandDescription = getBrandDescription(clientOpenai, brandName, brandWebsite, brandCountry)
    brandIndustry = getBrandIndustry(clientOpenai, brandName, brandWebsite, brandDescription, brandCountry)
    brandCompetitors = getBrandCompetitors(clientOpenai, brandName, brandWebsite, brandDescription, brandIndustry, brandCountry)
    brandName = getBrandName(clientOpenai, brandDescription)
    
    return {
        "description": brandDescription,
        "industry": brandIndustry,
        "competitors": brandCompetitors,
        "name": brandName
    }