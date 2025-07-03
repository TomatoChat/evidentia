#!/usr/bin/env python3
"""
Perplexity AI Integration Example
================================

This example demonstrates how to use the Perplexity AI integration
alongside the existing OpenAI integration in the Evidentia project.

Requirements:
- Set PERPLEXITY_API_KEY environment variable
- Install required dependencies: pip install requests

Usage Examples:
1. Generate queries using Perplexity AI
2. Perform web search and analysis
3. Get comprehensive brand analysis
"""

import os
import sys
import json

# Add the backend libs directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import libs.perplexity as perplexityAnalytics
import libs.openai as openaiAnalytics

def demonstrate_query_generation():
    """
    Compare query generation between OpenAI and Perplexity
    """
    print("🔍 QUERY GENERATION COMPARISON")
    print("=" * 50)
    
    # Sample brand data
    brand_name = "Tesla"
    brand_country = "United States"
    brand_description = "Electric vehicle and clean energy company"
    brand_industry = "Automotive/Energy"
    total_queries = 5
    
    print(f"Brand: {brand_name}")
    print(f"Industry: {brand_industry}")
    print(f"Generating {total_queries} queries...\n")
    
    try:
        # Generate with Perplexity (with real-time web data)
        print("🤖 PERPLEXITY AI RESULTS:")
        print("-" * 25)
        perplexity_queries = perplexityAnalytics.getCoherentQueries(
            brand_name, brand_country, brand_description, brand_industry, total_queries
        )
        
        for i, query in enumerate(perplexity_queries.get('queries', []), 1):
            print(f"{i}. {query}")
        
    except Exception as e:
        print(f"❌ Perplexity Error: {e}")
    
    print("\n" + "=" * 50)
    
    try:
        # Generate with OpenAI for comparison
        print("🧠 OPENAI RESULTS:")
        print("-" * 18)
        openai_queries = openaiAnalytics.getCoherentQueries(
            brand_name, brand_country, brand_description, brand_industry, total_queries
        )
        
        for i, query in enumerate(openai_queries.get('queries', []), 1):
            print(f"{i}. {query}")
            
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")


def demonstrate_web_search():
    """
    Demonstrate Perplexity's web search capabilities
    """
    print("\n\n🌐 WEB SEARCH & ANALYSIS")
    print("=" * 50)
    
    query = "latest Tesla stock performance 2024"
    context = "Looking for recent financial performance and market trends"
    
    print(f"Query: {query}")
    print(f"Context: {context}\n")
    
    try:
        results = perplexityAnalytics.webSearchAndAnalyze(query, context)
        
        print("📊 SEARCH RESULTS:")
        print("-" * 20)
        print(f"Summary: {results.get('summary', 'N/A')}")
        print(f"Search Quality: {results.get('search_quality', 'N/A')}")
        print(f"Last Updated: {results.get('last_updated', 'N/A')}")
        
        print("\n🎯 KEY INSIGHTS:")
        for i, insight in enumerate(results.get('key_insights', []), 1):
            print(f"{i}. {insight}")
        
        print("\n📚 SOURCES:")
        for i, source in enumerate(results.get('sources', [])[:3], 1):
            print(f"{i}. {source.get('title', 'Unknown')}")
            print(f"   URL: {source.get('url', 'N/A')}")
            if source.get('snippet'):
                print(f"   Preview: {source['snippet'][:100]}...")
            print()
            
    except Exception as e:
        print(f"❌ Web Search Error: {e}")


def demonstrate_brand_analysis():
    """
    Demonstrate comprehensive brand analysis
    """
    print("\n\n🏢 BRAND ANALYSIS")
    print("=" * 50)
    
    brand_name = "Netflix"
    brand_website = "https://netflix.com"
    competitors = ["Disney+", "Hulu", "Amazon Prime Video"]
    
    print(f"Analyzing: {brand_name}")
    print(f"Website: {brand_website}")
    print(f"Competitors: {', '.join(competitors)}\n")
    
    try:
        analysis = perplexityAnalytics.getBrandAnalysis(
            brand_name, brand_website, competitors
        )
        
        print("📈 ANALYSIS RESULTS:")
        print("-" * 20)
        print(f"Overall Sentiment: {analysis.get('overall_sentiment', 'N/A')}")
        print(f"Market Position: {analysis.get('market_position', 'N/A')}")
        print(f"Reputation Score: {analysis.get('reputation_score', 'N/A')}")
        
        print("\n🆕 RECENT DEVELOPMENTS:")
        for dev in analysis.get('recent_developments', [])[:3]:
            print(f"• {dev}")
        
        print("\n🎯 COMPETITIVE ANALYSIS:")
        comp_analysis = analysis.get('competitive_analysis', {})
        print(f"Strengths: {len(comp_analysis.get('strengths', []))} identified")
        print(f"Opportunities: {len(comp_analysis.get('opportunities', []))} identified")
        
        print("\n💻 DIGITAL PRESENCE:")
        digital = analysis.get('digital_presence', {})
        print(f"Website Quality: {digital.get('website_quality', 'N/A')}")
        print(f"Social Media: {digital.get('social_media_activity', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Brand Analysis Error: {e}")


def check_api_keys():
    """
    Check if required API keys are set
    """
    print("🔑 API KEY STATUS")
    print("=" * 50)
    
    openai_key = os.getenv('OPENAI_API_KEY')
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    
    print(f"OpenAI API Key: {'✅ Set' if openai_key else '❌ Not Set'}")
    print(f"Perplexity API Key: {'✅ Set' if perplexity_key else '❌ Not Set'}")
    
    if not perplexity_key:
        print("\n⚠️  To use Perplexity features, set your API key:")
        print("export PERPLEXITY_API_KEY='your-perplexity-api-key-here'")
        return False
    
    return True


if __name__ == "__main__":
    print("🚀 EVIDENTIA - PERPLEXITY AI INTEGRATION DEMO")
    print("=" * 70)
    
    # Check API keys first
    if not check_api_keys():
        print("\n❌ Please set up your Perplexity API key to run this demo.")
        sys.exit(1)
    
    try:
        # Run demonstrations
        demonstrate_query_generation()
        demonstrate_web_search()
        demonstrate_brand_analysis()
        
        print("\n\n✅ Demo completed successfully!")
        print("You can now use Perplexity AI alongside OpenAI in your Evidentia workflows.")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)