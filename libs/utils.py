import sys
import os
import json
from typing import Any, Dict, List
from langchain.prompts import PromptTemplate
from openai import OpenAI
import libs.openai as openaiAnalytics
import re


with open('utils/countryLanguage.json', 'r', encoding='utf-8') as file:
    countryLanguages = json.load(file)

openAiDefaultModel: str = "gpt-4o-mini-2024-07-18"


def translateString(stringToTranslate: str, targetLanguage: str, openAiModel: str = openAiDefaultModel) -> str:
    """
    Translates a given string into the specified target language using an LLM (OpenAI) and a prompt template.
    
    Args:
        stringToTranslate (str): The text string to be translated.
        targetLanguage (str): The language to translate the string into.
        openAiModel (str, optional): The OpenAI model to use. Defaults to openAiDefaultModel.
    
    Returns:
        str: The translated string, or an empty string if translation fails.
    """
    return stringToTranslate

    llmClient = OpenAI()

    with open("prompts/translateString.txt", "r", encoding="utf-8") as file:
        promptTemplate = file.read()

    prompt = PromptTemplate(
        input_variables=["stringToTranslate", "targetLanguage"],
        template=promptTemplate
    ).format(
        stringToTranslate=stringToTranslate,
        targetLanguage=targetLanguage
    )
    response = llmClient.chat.completions.create(
        model=openAiModel,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content


def getBrandDescription(brandName: str, brandWebsite: str, brandCountry: str = "world", openAiModel: str = openAiDefaultModel, clientOpenai: Any = OpenAI()) -> str:
    """
    Retrieves the company description using OpenAI's responses API and the brandDescription prompt template.
    
    Args:
        clientOpenai (Any): An initialized OpenAI client instance.
        brandName (str): The name of the brand/company.
        brandWebsite (str): The website of the brand/company.
        brandCountry (str, optional): The country of the brand/company. Defaults to "world".
        openAiModel (str, optional): The OpenAI model to use. Defaults to openAiDefaultModel.
    
    Returns:
        str: The company description, translated if necessary.
    """
    with open("prompts/brandDescription.txt", "r", encoding="utf-8") as file:
        promptTemplate = file.read()
    
    prompt = PromptTemplate(
        input_variables=["companyName", "companyWebsite", "companyCountry"],
        template=promptTemplate
    ).format(
        companyName=brandName,
        companyWebsite=brandWebsite,
        companyCountry=brandCountry
    )
    targetLanguage = countryLanguages.get(brandCountry.lower(), 'english').lower()

    if targetLanguage != 'english':
        translatedPrompt = translateString(prompt, targetLanguage)

        if 'NULL' not in translatedPrompt:
            prompt = translatedPrompt

    try:
        response = clientOpenai.responses.create(
            model=openAiModel,
            input=prompt,
            temperature=0.7,
            timeout=30,
            tools=[{"type": "web_search_preview"}],
        )
        messagesAnnotations, messagesTexts = openaiAnalytics.getResponseInfo(response)
        result = next(iter(messagesTexts.values()), "")

        try:
            parsedResult = json.loads(result)
            description = parsedResult.get("description", "")

            if description and description.strip():
                return description
            else:
                fallbackDescription = f"{brandName} is a business operating in {brandCountry} with their website at {brandWebsite}. The company provides digital services and solutions to their customers in the local market."
                return fallbackDescription
        except json.JSONDecodeError:
            if result and result.strip() and result.strip().upper() != "NULL":
                return result
            else:
                fallbackDescription = f"{brandName} is a business operating in {brandCountry} with their website at {brandWebsite}. The company provides digital services and solutions to their customers in the local market."
                return fallbackDescription
    except Exception as e:
        print(f"Error in getBrandDescription: {e}")
        raise Exception(f"Failed to get brand description: {str(e)}")


def getBrandIndustry(brandName: str, brandWebsite: str, brandDescription: str, brandCountry: str = "world", openAiModel: str = openAiDefaultModel, clientOpenai: Any = OpenAI()) -> str:
    """
    Retrieves the company industry using OpenAI's responses API and the brandIndustry prompt template.
    
    Args:
        clientOpenai (Any): An initialized OpenAI client instance.
        brandName (str): The name of the brand/company.
        brandWebsite (str): The website of the brand/company.
        brandDescription (str): A description of the brand/company.
        brandCountry (str, optional): The country of the brand/company. Defaults to "world".
        openAiModel (str, optional): The OpenAI model to use. Defaults to openAiDefaultModel.
    
    Returns:
        str: The company industry as determined by the LLM, translated if necessary.
    """
    with open("prompts/brandIndustry.txt", "r", encoding="utf-8") as file:
        promptTemplate = file.read()

    prompt = PromptTemplate(
        input_variables=["companyName", "companyWebsite", "companyCountry", "companyDescription"],
        template=promptTemplate
    ).format(
        companyName=brandName,
        companyWebsite=brandWebsite,
        companyCountry=brandCountry,
        companyDescription=brandDescription
    )
    targetLanguage = countryLanguages.get(brandCountry.lower(), 'english').lower()

    if targetLanguage != 'english':
        translatedPrompt = translateString(prompt, targetLanguage)

        if 'NULL' not in translatedPrompt:
            prompt = translatedPrompt
    try:
        response = clientOpenai.responses.create(
            model=openAiModel,
            input=prompt,
            temperature=0.7,
            timeout=30,
            tools=[{"type": "web_search_preview"}],
        )
        messagesAnnotations, messagesTexts = openaiAnalytics.getResponseInfo(response)
        result = next(iter(messagesTexts.values()), "")

        if not result or result.strip() == "":
            raise ValueError("Empty response received from OpenAI API")
        return result
    except Exception as e:
        print(f"Error in getBrandIndustry: {e}")
        raise Exception(f"Failed to get brand industry: {str(e)}")


def getBrandCompetitors(brandName: str, brandWebsite: str, brandDescription: str, brandIndustry: str, brandCountry: str = "world", openAiModel: str = openAiDefaultModel, clientOpenai: Any = OpenAI()) -> Dict[str, Any]:
    """
    Retrieves the company's competitors using OpenAI's responses API and the brandCompetitors prompt template.
    
    Args:
        clientOpenai (Any): An initialized OpenAI client instance.
        brandName (str): The name of the brand/company.
        brandWebsite (str): The website of the brand/company.
        brandDescription (str): A description of the brand/company.
        brandIndustry (str): The industry in which the brand/company operates.
        brandCountry (str, optional): The country of the brand/company. Defaults to "world".
        openAiModel (str, optional): The OpenAI model to use. Defaults to openAiDefaultModel.
    
    Returns:
        Dict[str, Any]: A dictionary containing the competitors, parsed from the JSON response.
    """
    with open("prompts/brandCompetitors.txt", "r", encoding="utf-8") as file:
        promptTemplate = file.read()
    
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
    targetLanguage = countryLanguages.get(brandCountry.lower(), 'english').lower()

    if targetLanguage != 'english':
        translatedPrompt = translateString(prompt, targetLanguage)

        if 'NULL' not in translatedPrompt:
            prompt = translatedPrompt
    try:
        response = clientOpenai.responses.create(
            model=openAiModel,
            input=prompt,
            temperature=0.7,
            timeout=30,
            tools=[{"type": "web_search_preview"}],
        )
        messagesAnnotations, messagesTexts = openaiAnalytics.getResponseInfo(response)
        rawJson = next(iter(messagesTexts.values()), "")

        if rawJson.startswith("```json"):
            rawJson = rawJson[len("```json"):].strip()

        if rawJson.endswith("```"):
            rawJson = rawJson[:-3].strip()

        if not rawJson.strip():
            raise ValueError("No JSON output received from OpenAI API.")
        
        return json.loads(rawJson)
    except Exception as e:
        print(f"Error in getBrandCompetitors: {e}")
        return {"competitors": []}


def getBrandName(brandDescription: str, openAiModel: str = openAiDefaultModel, clientOpenai: Any = OpenAI()) -> str:
    """
    Retrieves the company name using OpenAI's responses API and the brandName prompt template.
    
    Args:
        clientOpenai (Any): An initialized OpenAI client instance.
        brandDescription (str): A description of the brand/company.
        openAiModel (str, optional): The OpenAI model to use. Defaults to openAiDefaultModel.
    
    Returns:
        str: The company name as determined by the LLM.
    """
    with open("prompts/brandName.txt", "r", encoding="utf-8") as file:
        promptTemplate = file.read()

    prompt = PromptTemplate(
        input_variables=["companyDescription"],
        template=promptTemplate
    ).format(
        companyDescription=brandDescription
    )

    try:
        response = clientOpenai.responses.create(
            model=openAiModel,
            input=prompt,
            temperature=0.7,
            timeout=30,
            tools=[{"type": "web_search_preview"}],
        )
        messagesAnnotations, messagesTexts = openaiAnalytics.getResponseInfo(response)
        rawJson = next(iter(messagesTexts.values()), "")

        if rawJson.startswith("```json"):
            rawJson = rawJson[len("```json"):].strip()

        if rawJson.endswith("```"):
            rawJson = rawJson[:-3].strip()

        if not rawJson.strip():
            raise ValueError("No JSON output received from OpenAI API.")
        
        return json.loads(rawJson)
    except Exception as e:
        print(f"Error in getBrandName: {e}")
        raise Exception(f"Failed to get brand name: {str(e)}")


def getCompanyInfo(brandName: str, brandWebsite: str, brandCountry: str = "world") -> Dict[str, Any]:
    """
    Retrieves the company description, industry, competitors, and name using OpenAI's responses API and prompt templates.
    
    Args:
        brandName (str): The name of the brand/company.
        brandWebsite (str): The website of the brand/company.
        brandCountry (str, optional): The country of the brand/company. Defaults to "world".
    
    Returns:
        Dict[str, Any]: A dictionary with keys 'description', 'industry', 'competitors', and 'name'.
    """    
    clientOpenai = OpenAI()
    brandDescription = getBrandDescription(brandName, brandWebsite, brandCountry, clientOpenai=clientOpenai)
    brandIndustry = getBrandIndustry(brandName, brandWebsite, brandDescription, brandCountry, clientOpenai=clientOpenai)
    brandCompetitors = getBrandCompetitors(brandName, brandWebsite, brandDescription, brandIndustry, brandCountry, clientOpenai=clientOpenai)
    brandName = getBrandName(brandDescription, clientOpenai=clientOpenai)

    return {
        "description": brandDescription,
        "industry": brandIndustry,
        "competitors": brandCompetitors,
        "name": brandName
    }


def formatQueryAnalysis(rawAnalysis: str) -> str:
    """
    Formats raw query analysis output into a readable markdown format.
    
    Args:
        rawAnalysis (str): Raw query analysis text.
    
    Returns:
        str: Formatted markdown analysis report.
    """
    lines = rawAnalysis.strip().split('\n')
    formattedOutput = []
    formattedOutput.append("# 𝄞F4CA Detailed Query Analysis Report\n")
    brandMatch = re.search(r'Context:.*?mention of (?:the brand )?([A-Z][a-z]+)', rawAnalysis)
    brandName = brandMatch.group(1) if brandMatch else "Brand"
    queryCount = len([line for line in lines if line.startswith('❌') or line.startswith('✅')])

    formattedOutput.append("## Query Performance Summary")
    formattedOutput.append(f"- **Total Queries Tested**: {queryCount}")
    formattedOutput.append("- **LLM Model**: gpt-4o-mini-2024-07-18")
    formattedOutput.append(f"- **Brand**: {brandName}")
    formattedOutput.append("- **Overall Performance**: ❌ No mentions detected\n")
    formattedOutput.append("---\n")
    formattedOutput.append("## 𝄞F50D Individual Query Results\n")

    queryNum = 1
    currentQuery = {}

    for line in lines:
        line = line.strip()

        if line.startswith('❌') or line.startswith('✅'):
            statusIcon = '❌' if line.startswith('❌') else '✅'
            topicMatch = re.search(r"'topic': '([^']+)'", line)
            promptMatch = re.search(r"'prompt': '([^']+)'", line)
            modelMatch = re.search(r'\(([^)]+)\)', line)
            topic = topicMatch.group(1) if topicMatch else f"Query {queryNum}"
            prompt = promptMatch.group(1) if promptMatch else "No prompt available"
            model = modelMatch.group(1) if modelMatch else "gpt-4o-mini-2024-07-18"
            currentQuery = {
                'status_icon': statusIcon,
                'topic': topic,
                'prompt': prompt,
                'model': model,
                'number': queryNum
            }
        elif line.startswith('Not mentioned') or line.startswith('Mentioned'):
            parts = line.split('|')
            status = parts[0].strip()
            sentiment = parts[1].strip().replace('Sentiment: ', '') if len(parts) > 1 else 'neutral'
            currentQuery['status'] = status
            currentQuery['sentiment'] = sentiment
        elif line.startswith('Context:'):
            currentQuery['context'] = line.replace('Context: ', '').strip()
        elif line.startswith('LLM Response:'):
            currentQuery['response'] = line.replace('LLM Response: ', '').strip()

            if 'topic' in currentQuery:
                formattedOutput.append(f"### Query #{currentQuery['number']}: {currentQuery['topic']}")
                formattedOutput.append(f"**Prompt**: \"{currentQuery['prompt']}\"\n")
                formattedOutput.append("| Metric | Result |")
                formattedOutput.append("|--------|--------|")
                formattedOutput.append(f"| **Status** | {currentQuery['status_icon']} {currentQuery['status']} |")
                sentimentIcon = "😊" if "positive" in currentQuery['sentiment'] else "😐" if "neutral" in currentQuery['sentiment'] else "😞"
                formattedOutput.append(f"| **Sentiment** | {sentimentIcon} {currentQuery['sentiment'].title()} |")
                formattedOutput.append(f"| **Brand Context** | {currentQuery.get('context', 'No context available')} |\n")
                formattedOutput.append("**LLM Response Preview**:")
                responsePreview = currentQuery['response'][:100] + "..." if len(currentQuery['response']) > 100 else currentQuery['response']
                formattedOutput.append(f"> {responsePreview}\n")
                if currentQuery['status_icon'] == '❌':
                    formattedOutput.append(f"**Analysis**: The query did not mention {brandName}, indicating low brand awareness for this search intent. Consider optimizing content for this topic area.\n")
                else:
                    formattedOutput.append(f"**Analysis**: {brandName} was mentioned, showing good brand visibility for this query type.\n")
                formattedOutput.append("---\n")
                queryNum += 1
                currentQuery = {}

    formattedOutput.append("## 𝄞F4C8 Optimization Recommendations\n")
    formattedOutput.append("1. **🎯 Content Strategy**: Create targeted content addressing the query topics where brand wasn't mentioned")
    formattedOutput.append("2. **🔍 SEO & GEO Optimization**: Optimize for the specific phrases and contexts tested")
    formattedOutput.append("3. **📝 Thought Leadership**: Develop authoritative content in relevant topic areas")
    formattedOutput.append("4. **🤝 Industry Presence**: Increase visibility in industry discussions and platforms")
    formattedOutput.append("5. **📊 Regular Monitoring**: Set up regular GEO monitoring for these query types")

    return '\n'.join(formattedOutput)


def extractMentionedBrands(llmOutput: str, openAiModel: str = openAiDefaultModel) -> List[Dict[str, Any]]:
    """
    Extracts mentioned brands from the LLM output using a prompt and OpenAI API.
    
    Args:
        llmOutput (str): The output string from the LLM to analyze.
        openAiModel (str, optional): The OpenAI model to use. Defaults to openAiDefaultModel.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries with extracted brand information.
    """
    llmClient = OpenAI()

    with open("prompts/extractBrandsAndInfo.txt", "r", encoding="utf-8") as file:
        promptTemplate = file.read()

    prompt = PromptTemplate(
        input_variables=["llmOutput"],
        template=promptTemplate
    ).format(
        llmOutput=llmOutput,
    )
    response = llmClient.chat.completions.create(
        model=openAiModel,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    rawJson = response.choices[0].message.content

    if rawJson.startswith("```json"):
        rawJson = rawJson[len("```json"):].strip()

    if rawJson.endswith("```"):
        rawJson = rawJson[:-3].strip()

    if not rawJson.strip():
        raise ValueError("No JSON output received from OpenAI API.")

    try:
        return json.loads(rawJson)
    except json.JSONDecodeError:
        # Try to extract the first JSON array from the string
        match = re.search(r'\\[.*\\]', rawJson, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        print("Malformed JSON from LLM:\n", rawJson)
        raise