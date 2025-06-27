import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Also try loading from explicit path
load_dotenv(dotenv_path='.env', override=True)

from flask import Flask, request, jsonify, render_template
import libs.utils as utils
import libs.openai as openaiAnalytics
import libs.search_analysis as search_analysis

app = Flask(__name__)

# Print environment variables for debugging
print("=== Environment Variables ===")
api_key = os.getenv('OPENAI_API_KEY', 'NOT SET')
print(f"OPENAI_API_KEY: {api_key[:10] if api_key != 'NOT SET' else 'NOT SET'}{'*' * 20 if api_key != 'NOT SET' else ''}")
print(f"PROJECT_DIRECTORY: {os.getenv('PROJECT_DIRECTORY', 'NOT SET')}")
print(f"Current working directory: {os.getcwd()}")
print(f"API key length: {len(api_key) if api_key != 'NOT SET' else 0}")
print("=============================")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/brand-info', methods=['POST'])
def get_brand_info():
    try:
        data = request.json
        brand_name = data.get('brandName')
        brand_website = data.get('brandWebsite')
        brand_country = data.get('brandCountry', 'world')
        
        if not brand_name or not brand_website:
            return jsonify({'error': 'brandName and brandWebsite are required'}), 400
        
        brand_information = utils.getCompanyInfo(brand_name, brand_website, brand_country)
        return jsonify(brand_information)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-queries', methods=['POST'])
def generate_queries():
    try:
        data = request.json
        brand_name = data.get('brandName')
        brand_country = data.get('brandCountry', 'world')
        brand_description = data.get('brandDescription')
        brand_industry = data.get('brandIndustry')
        total_queries = data.get('totalQueries', 10)
        
        if not all([brand_name, brand_description, brand_industry]):
            return jsonify({'error': 'brandName, brandDescription, and brandIndustry are required'}), 400
        
        queries = openaiAnalytics.getCoherentQueries(
            brand_name, brand_country, brand_description, brand_industry, total_queries
        )
        return jsonify({'queries': queries})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test-queries', methods=['POST'])
def test_queries():
    try:
        data = request.json
        brand_name = data.get('brandName')
        queries = data.get('queries', [])
        competitors = data.get('competitors', [])
        locations = data.get('locations', ['United States'])
        
        if not brand_name or not queries:
            return jsonify({'error': 'brandName and queries are required'}), 400
        
        # Extract query strings from query objects if needed
        query_strings = []
        for q in queries:
            if isinstance(q, dict):
                query_strings.append(q.get('query', str(q)))
            else:
                query_strings.append(str(q))
        
        analysis = search_analysis.analyze_brand_presence(
            brand_name, competitors, query_strings, locations
        )
        return jsonify(analysis)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-locations', methods=['GET'])
def get_locations():
    try:
        locations = search_analysis.generate_geo_locations()
        return jsonify({'locations': locations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-search-suggestions', methods=['POST'])
def get_search_suggestions():
    try:
        data = request.json
        brand_name = data.get('brandName')
        industry = data.get('industry', '')
        
        if not brand_name:
            return jsonify({'error': 'brandName is required'}), 400
        
        suggestions = search_analysis.get_search_suggestions(brand_name, industry)
        return jsonify({'suggestions': suggestions})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)