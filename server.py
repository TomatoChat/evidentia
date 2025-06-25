from flask import Flask, request, jsonify, render_template_string
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project directory to path
if os.getenv("PROJECT_DIRECTORY"):
    os.chdir(os.getenv("PROJECT_DIRECTORY"))
    sys.path.append(os.getenv("PROJECT_DIRECTORY"))

import libs.utils as utils
import libs.openai as openaiAnalytics

app = Flask(__name__)

# HTML template for the frontend
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brand Research Tool</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        input[type="text"], input[type="number"], select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        .results {
            margin-top: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
            display: none;
        }
        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
        }
        .error {
            color: #dc3545;
            background-color: #f8d7da;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }
        .section {
            margin-bottom: 20px;
        }
        .section h3 {
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 5px;
        }
        .query-item {
            background: white;
            padding: 10px;
            margin: 5px 0;
            border-left: 3px solid #007bff;
            border-radius: 3px;
        }
        .query-topic {
            font-weight: bold;
            color: #007bff;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Brand Research Tool</h1>
        
        <form id="brandForm">
            <div class="form-group">
                <label for="brandName">Brand Name:</label>
                <input type="text" id="brandName" name="brandName" required>
            </div>
            
            <div class="form-group">
                <label for="brandWebsite">Brand Website:</label>
                <input type="text" id="brandWebsite" name="brandWebsite" placeholder="example.com" required>
            </div>
            
            <div class="form-group">
                <label for="brandCountry">Brand Country:</label>
                <select id="brandCountry" name="brandCountry">
                    <option value="world">World</option>
                    <option value="afghanistan">Afghanistan</option>
                    <option value="albania">Albania</option>
                    <option value="algeria">Algeria</option>
                    <option value="argentina">Argentina</option>
                    <option value="australia">Australia</option>
                    <option value="austria">Austria</option>
                    <option value="bangladesh">Bangladesh</option>
                    <option value="belgium">Belgium</option>
                    <option value="brazil">Brazil</option>
                    <option value="canada">Canada</option>
                    <option value="china">China</option>
                    <option value="colombia">Colombia</option>
                    <option value="denmark">Denmark</option>
                    <option value="egypt">Egypt</option>
                    <option value="finland">Finland</option>
                    <option value="france">France</option>
                    <option value="germany">Germany</option>
                    <option value="greece">Greece</option>
                    <option value="india">India</option>
                    <option value="indonesia">Indonesia</option>
                    <option value="iran">Iran</option>
                    <option value="iraq">Iraq</option>
                    <option value="ireland">Ireland</option>
                    <option value="israel">Israel</option>
                    <option value="italy">Italy</option>
                    <option value="japan">Japan</option>
                    <option value="kenya">Kenya</option>
                    <option value="mexico">Mexico</option>
                    <option value="netherlands">Netherlands</option>
                    <option value="new zealand">New Zealand</option>
                    <option value="nigeria">Nigeria</option>
                    <option value="norway">Norway</option>
                    <option value="pakistan">Pakistan</option>
                    <option value="peru">Peru</option>
                    <option value="philippines">Philippines</option>
                    <option value="poland">Poland</option>
                    <option value="portugal">Portugal</option>
                    <option value="russia">Russia</option>
                    <option value="saudi arabia">Saudi Arabia</option>
                    <option value="south africa">South Africa</option>
                    <option value="south korea">South Korea</option>
                    <option value="spain">Spain</option>
                    <option value="sweden">Sweden</option>
                    <option value="switzerland">Switzerland</option>
                    <option value="thailand">Thailand</option>
                    <option value="turkey">Turkey</option>
                    <option value="united kingdom">United Kingdom</option>
                    <option value="united states">United States</option>
                    <option value="vietnam">Vietnam</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="totalQueries">Number of Queries to Generate:</label>
                <input type="number" id="totalQueries" name="totalQueries" value="10" min="1" max="50">
            </div>
            
            <button type="submit">Analyze Brand</button>
        </form>
        
        <div id="results" class="results">
            <div id="loading" class="loading" style="display: none;">
                Analyzing brand... This may take a few minutes.
            </div>
            <div id="content"></div>
        </div>
    </div>

    <script>
        document.getElementById('brandForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            const submitBtn = e.target.querySelector('button[type="submit"]');
            const resultsDiv = document.getElementById('results');
            const loadingDiv = document.getElementById('loading');
            const contentDiv = document.getElementById('content');
            
            // Show loading state
            submitBtn.disabled = true;
            resultsDiv.style.display = 'block';
            loadingDiv.style.display = 'block';
            contentDiv.innerHTML = '';
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.error) {
                    contentDiv.innerHTML = '<div class="error">Error: ' + result.error + '</div>';
                } else {
                    displayResults(result);
                }
            } catch (error) {
                contentDiv.innerHTML = '<div class="error">Error: ' + error.message + '</div>';
            } finally {
                loadingDiv.style.display = 'none';
                submitBtn.disabled = false;
            }
        });
        
        function displayResults(data) {
            const contentDiv = document.getElementById('content');
            
            let html = '';
            
            // Brand Information
            html += '<div class="section">';
            html += '<h3>Brand Information</h3>';
            html += '<p><strong>Name:</strong> ' + (data.brandInfo.name || 'N/A') + '</p>';
            html += '<p><strong>Industry:</strong> ' + (data.brandInfo.industry || 'N/A') + '</p>';
            html += '<p><strong>Description:</strong> ' + (data.brandInfo.description || 'N/A') + '</p>';
            html += '</div>';
            
            // Competitors
            if (data.brandInfo.competitors && data.brandInfo.competitors.length > 0) {
                html += '<div class="section">';
                html += '<h3>Competitors</h3>';
                data.brandInfo.competitors.forEach(competitor => {
                    html += '<div class="query-item">';
                    html += '<div class="query-topic">' + competitor.name + '</div>';
                    html += '<div>' + competitor.description + '</div>';
                    html += '</div>';
                });
                html += '</div>';
            }
            
            // Generated Queries
            if (data.queries && data.queries.length > 0) {
                html += '<div class="section">';
                html += '<h3>Generated Search Queries</h3>';
                data.queries.forEach(query => {
                    html += '<div class="query-item">';
                    html += '<div class="query-topic">' + query.topic + '</div>';
                    html += '<div>' + query.prompt + '</div>';
                    html += '</div>';
                });
                html += '</div>';
            }
            
            contentDiv.innerHTML = html;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main HTML interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze_brand():
    """Analyze brand and generate queries"""
    try:
        data = request.get_json()
        
        brand_name = data.get('brandName', '').strip()
        brand_website = data.get('brandWebsite', '').strip()
        brand_country = data.get('brandCountry', 'world').strip()
        total_queries = int(data.get('totalQueries', 10))
        
        if not brand_name or not brand_website:
            return jsonify({'error': 'Brand name and website are required'}), 400
        
        # Get company information
        brand_info = utils.getCompanyInfo(brand_name, brand_website, brand_country)
        
        # Generate queries
        queries = openaiAnalytics.getCoherentQueries(
            brand_info['name'], 
            brand_country, 
            brand_info['description'], 
            brand_info['industry'], 
            total_queries
        )
        
        return jsonify({
            'brandInfo': brand_info,
            'queries': queries
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Check if required environment variables are set
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY environment variable not set")
    
    app.run(debug=True, host='0.0.0.0', port=5000)