import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Also try loading from explicit path
load_dotenv(dotenv_path='.env', override=True)

from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS
import json
import time
import libs.utils as utils
import libs.openai as openaiAnalytics
import libs.perplexity as perplexityAnalytics
import libs.geo_analysis as geo_analysis
import libs.search_analysis as search_analysis
import libs.email_service as email_service
from libs.convex_client import get_convex_client

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Convex client
try:
    convex_client = get_convex_client()
    print("✅ Convex client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Convex client: {e}")
    convex_client = None

# In-memory storage for user emails (fallback if Convex fails)
user_emails = {}

# Print environment variables for debugging
print("=== Environment Variables ===")
api_key = os.getenv('OPENAI_API_KEY', 'NOT SET')
print(f"OPENAI_API_KEY: {api_key[:10] if api_key != 'NOT SET' else 'NOT SET'}{'*' * 20 if api_key != 'NOT SET' else ''}")
perplexity_key = os.getenv('PERPLEXITY_API_KEY', 'NOT SET')
print(f"PERPLEXITY_API_KEY: {perplexity_key[:10] if perplexity_key != 'NOT SET' else 'NOT SET'}{'*' * 20 if perplexity_key != 'NOT SET' else ''}")
convex_url = os.getenv('CONVEX_URL', 'NOT SET')
print(f"CONVEX_URL: {convex_url[:20] if convex_url != 'NOT SET' else 'NOT SET'}{'*' * 10 if convex_url != 'NOT SET' else ''}")
smtp_email = os.getenv('SMTP_EMAIL', 'NOT SET')
print(f"SMTP_EMAIL: {smtp_email[:10] if smtp_email != 'NOT SET' else 'NOT SET'}{'*' * 10 if smtp_email != 'NOT SET' else ''}")
smtp_password = os.getenv('SMTP_PASSWORD', 'NOT SET')
print(f"SMTP_PASSWORD: {'SET' if smtp_password != 'NOT SET' else 'NOT SET'}")
print(f"PROJECT_DIRECTORY: {os.getenv('PROJECT_DIRECTORY', 'NOT SET')}")
print(f"Current working directory: {os.getcwd()}")
print(f"OpenAI API key length: {len(api_key) if api_key != 'NOT SET' else 0}")
print(f"Perplexity API key length: {len(perplexity_key) if perplexity_key != 'NOT SET' else 0}")
print("=============================")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifesto')
def manifesto():
    return render_template('manifesto.html')

@app.route('/api')
def api_info():
    return jsonify({
        'message': 'Evidentia API Server',
        'status': 'running',
        'version': '1.0.0',
        'endpoints': [
            '/collect-email',
            '/stream-brand-info',
            '/stream-generate-queries', 
            '/stream-test-queries',
            '/perplexity-generate-queries',
            '/perplexity-web-search',
            '/perplexity-brand-analysis',
            '/send-report',
            '/get-llm-models',
            '/health'
        ]
    })

@app.route('/collect-email', methods=['POST'])
def collect_email():
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Try to use Convex, fallback to in-memory storage
        if convex_client:
            try:
                session_id = convex_client.create_session(email)
                print(f"Collected email: {email} with session ID: {session_id} (stored in Convex)")
            except Exception as e:
                print(f"Convex error, falling back to in-memory: {e}")
                import uuid
                session_id = str(uuid.uuid4())
                user_emails[session_id] = email
                print(f"Collected email: {email} with session ID: {session_id} (stored in memory)")
        else:
            # Fallback to in-memory storage
            import uuid
            session_id = str(uuid.uuid4())
            user_emails[session_id] = email
            print(f"Collected email: {email} with session ID: {session_id} (stored in memory - no Convex)")
        
        return jsonify({
            'success': True, 
            'message': 'Email collected successfully',
            'session_id': session_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/get-llm-models', methods=['GET'])
def get_llm_models():
    try:
        models = ["gpt-4o-mini-2024-07-18", "gpt-3.5-turbo", "gpt-4-turbo"]
        return jsonify({'models': models})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-llm-suggestions', methods=['POST'])
def get_llm_suggestions():
    try:
        data = request.json
        brand_name = data.get('brandName')
        industry = data.get('industry', '')
        
        if not brand_name:
            return jsonify({'error': 'brandName is required'}), 400
        
        suggestions = geo_analysis.generate_llm_test_queries(brand_name, industry)
        return jsonify({'suggestions': suggestions})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stream-brand-info', methods=['POST'])
def stream_brand_info():
    # Get request data outside the generator function
    data = request.json
    brand_name = data.get('brandName')
    brand_website = data.get('brandWebsite')
    brand_country = data.get('brandCountry', 'world')
    session_id = data.get('session_id')  # Get session_id to save results
    
    def generate():
        try:
            
            if not brand_name or not brand_website:
                yield f"data: {json.dumps({'error': 'brandName and brandWebsite are required'})}\n\n"
                return
            
            yield f"data: {json.dumps({'status': 'Starting brand analysis...', 'step': 'init'})}\n\n"
            time.sleep(0.1)
            
            yield f"data: {json.dumps({'status': 'Getting brand description...', 'step': 'description'})}\n\n"
            api_key = os.getenv("OPENAI_API_KEY")
            from openai import OpenAI
            client_openai = OpenAI(api_key=api_key)
            brand_description = utils.getBrandDescription(client_openai, brand_name, brand_website, brand_country)
            
            yield f"data: {json.dumps({'status': 'Analyzing industry...', 'step': 'industry'})}\n\n"
            brand_industry = utils.getBrandIndustry(client_openai, brand_name, brand_website, brand_description, brand_country)
            
            yield f"data: {json.dumps({'status': 'Finding competitors...', 'step': 'competitors'})}\n\n"
            brand_competitors = utils.getBrandCompetitors(client_openai, brand_name, brand_website, brand_description, brand_industry, brand_country)
            
            yield f"data: {json.dumps({'status': 'Extracting brand name...', 'step': 'name'})}\n\n"
            final_brand_name = utils.getBrandName(client_openai, brand_description)
            
            result = {
                "description": brand_description,
                "industry": brand_industry,
                "competitors": brand_competitors,
                "name": final_brand_name
            }
            
            # Save to Convex if available and session_id provided
            if convex_client and session_id:
                try:
                    convex_client.save_brand_analysis(
                        session_id=session_id,
                        brand_name=final_brand_name,
                        brand_website=brand_website,
                        brand_country=brand_country,
                        brand_description=brand_description,
                        brand_industry=brand_industry,
                        competitors=brand_competitors,
                        status="completed",
                        result_data=result
                    )
                    print(f"✅ Brand analysis saved to Convex for session {session_id}")
                except Exception as e:
                    print(f"❌ Failed to save brand analysis to Convex: {e}")
            
            yield f"data: {json.dumps({'status': 'Analysis complete!', 'step': 'complete', 'result': result})}\n\n"
            
        except Exception as e:
            error_msg = f"Brand analysis error: {str(e)}"
            print(f"ERROR in stream_brand_info: {error_msg}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/stream-generate-queries', methods=['POST'])
def stream_generate_queries():
    # Get request data outside the generator function
    data = request.json
    brand_name = data.get('brandName')
    brand_country = data.get('brandCountry', 'world')
    brand_description = data.get('brandDescription')
    brand_industry = data.get('brandIndustry')
    total_queries = data.get('totalQueries', 10)
    
    def generate():
        try:
            
            if not all([brand_name, brand_description, brand_industry]):
                yield f"data: {json.dumps({'error': 'brandName, brandDescription, and brandIndustry are required'})}\n\n"
                return
            
            yield f"data: {json.dumps({'status': 'Preparing query generation...', 'step': 'init'})}\n\n"
            time.sleep(0.1)
            
            yield f"data: {json.dumps({'status': f'Generating {total_queries} coherent queries...', 'step': 'generating'})}\n\n"
            queries = openaiAnalytics.getCoherentQueries(
                brand_name, brand_country, brand_description, brand_industry, total_queries
            )
            
            yield f"data: {json.dumps({'status': 'Query generation complete!', 'step': 'complete', 'result': {'queries': queries}})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/stream-test-queries', methods=['POST'])
def stream_test_queries():
    # Get request data outside the generator function
    data = request.json
    brand_name = data.get('brandName')
    queries = data.get('queries', [])
    competitors = data.get('competitors', [])
    llm_models = data.get('models', ['gpt-4o-mini-2024-07-18'])
    session_id = data.get('session_id')  # Add session_id for database saving
    
    def generate():
        try:
            if not brand_name or not queries:
                yield f"data: {json.dumps({'error': 'brandName and queries are required'})}\n\n"
                return
            
            # Extract query strings from query objects if needed
            query_strings = []
            for q in queries:
                if isinstance(q, dict):
                    query_strings.append(q.get('query', str(q)))
                else:
                    query_strings.append(str(q))
            
            yield f"data: {json.dumps({'status': f'Starting GEO analysis for {len(query_strings)} queries across {len(llm_models)} LLM models...', 'step': 'init', 'progress': 0})}\n\n"
            
            # Use the regular (non-streaming) geo_analysis function for now
            analysis_results = geo_analysis.analyze_llm_brand_positioning(
                brand_name=brand_name,
                competitors=competitors,
                queries=query_strings,
                llm_models=llm_models
            )
            
            yield f"data: {json.dumps({'status': 'GEO analysis computation complete!', 'step': 'analysis_complete', 'progress': 85})}\n\n"
            
            # Generate optimization suggestions
            yield f"data: {json.dumps({'status': 'Generating optimization suggestions...', 'step': 'suggestions', 'progress': 95})}\n\n"
            suggestions = geo_analysis.get_geo_optimization_suggestions(analysis_results)
            analysis_results["optimization_suggestions"] = suggestions
            
            # Save GEO analysis to Convex if available and session_id provided
            if convex_client and session_id:
                try:
                    convex_client.save_geo_analysis(
                        session_id=session_id,
                        brand_name=brand_name,
                        search_queries=query_strings,
                        competitors=competitors,
                        llm_models=llm_models,
                        optimization_suggestions="\n".join(suggestions) if isinstance(suggestions, list) else str(suggestions),
                        progress_status=100,
                        analysis_result=analysis_results,
                        status="completed"
                    )
                    print(f"✅ GEO analysis saved to Convex for session {session_id}")
                except Exception as e:
                    print(f"❌ Failed to save GEO analysis to Convex: {e}")
            
            yield f"data: {json.dumps({'status': 'GEO Analysis complete!', 'step': 'complete', 'progress': 100, 'result': analysis_results})}\n\n"
            
        except Exception as e:
            print(f"Error in stream_test_queries: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/web-search', methods=['POST'])
def web_search():
    try:
        data = request.json
        query = data.get('query')
        context = data.get('context', '')
        
        if not query:
            return jsonify({'error': 'query is required'}), 400
        
        search_results = openaiAnalytics.webSearchAndAnalyze(query, context)
        return jsonify(search_results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stream-web-search', methods=['POST'])
def stream_web_search():
    # Get request data outside the generator function
    data = request.json
    query = data.get('query')
    context = data.get('context', '')
    
    def generate():
        try:
            if not query:
                yield f"data: {json.dumps({'error': 'query is required'})}\n\n"
                return
            
            yield f"data: {json.dumps({'status': 'Initializing web search...', 'step': 'init'})}\n\n"
            time.sleep(0.1)
            
            yield f"data: {json.dumps({'status': f'Searching for: {query}', 'step': 'searching'})}\n\n"
            
            # Perform the web search and analysis
            search_results = openaiAnalytics.webSearchAndAnalyze(query, context)
            
            if 'error' in search_results:
                yield f"data: {json.dumps({'error': search_results['error'], 'step': 'error'})}\n\n"
                return
            
            yield f"data: {json.dumps({'status': 'Processing search results...', 'step': 'processing'})}\n\n"
            time.sleep(0.2)
            
            yield f"data: {json.dumps({'status': 'Analyzing findings...', 'step': 'analyzing'})}\n\n"
            time.sleep(0.2)
            
            yield f"data: {json.dumps({'status': 'Web search complete!', 'step': 'complete', 'result': search_results})}\n\n"
            
        except Exception as e:
            error_msg = f"Web search error: {str(e)}"
            print(f"ERROR in stream_web_search: {error_msg}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/format-query-analysis', methods=['POST'])
def format_query_analysis():
    try:
        data = request.json
        raw_analysis = data.get('rawAnalysis')
        
        if not raw_analysis:
            return jsonify({'error': 'rawAnalysis is required'}), 400
        
        formatted_analysis = utils.formatQueryAnalysis(raw_analysis)
        return jsonify({'formatted_analysis': formatted_analysis})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/send-report', methods=['POST'])
def send_report():
    try:
        data = request.json
        session_id = data.get('session_id')
        brand_name = data.get('brandName', 'Your Brand')
        analysis_result = data.get('analysisResult', {})
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        if not analysis_result:
            return jsonify({'error': 'Analysis result is required'}), 400
        
        # Get the email for this session from Convex first, then fallback to in-memory
        recipient_email = None
        if convex_client:
            try:
                session = convex_client.get_session(session_id)
                if session:
                    recipient_email = session.get('email')
            except Exception as e:
                print(f"Error getting session from Convex: {e}")
        
        # Fallback to in-memory storage
        if not recipient_email:
            recipient_email = user_emails.get(session_id)
        
        if not recipient_email:
            return jsonify({'error': 'Email not found for this session'}), 400
        
        # Send the email
        success = email_service.send_report_email(
            recipient_email=recipient_email,
            brand_name=brand_name,
            analysis_result=analysis_result
        )
        
        if success:
            # Save report to Convex
            if convex_client:
                try:
                    convex_client.save_report(
                        session_id=session_id,
                        report_type="combined",
                        report_data=analysis_result,
                        email_sent=True,
                        recipient_email=recipient_email,
                        brand_name=brand_name
                    )
                    print(f"✅ Report saved to Convex for session {session_id}")
                except Exception as e:
                    print(f"❌ Failed to save report to Convex: {e}")
            
            # Clean up the session after successful send
            if session_id in user_emails:
                del user_emails[session_id]
            
            # Clean up session from Convex as well
            if convex_client:
                try:
                    convex_client.delete_session(session_id)
                    print(f"✅ Session {session_id} cleaned up from Convex")
                except Exception as e:
                    print(f"❌ Failed to clean up session from Convex: {e}")
            
            return jsonify({
                'success': True, 
                'message': f'Report sent successfully to {recipient_email}'
            })
        else:
            return jsonify({'error': 'Failed to send email'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

@app.route('/perplexity-generate-queries', methods=['POST'])
def perplexity_generate_queries():
    try:
        data = request.json
        brand_name = data.get('brandName')
        brand_country = data.get('brandCountry', 'world')
        brand_description = data.get('brandDescription')
        brand_industry = data.get('brandIndustry')
        total_queries = data.get('totalQueries', 10)
        session_id = data.get('session_id')  # Add session_id for database saving
        
        if not all([brand_name, brand_description, brand_industry]):
            return jsonify({'error': 'brandName, brandDescription, and brandIndustry are required'}), 400
        
        queries = perplexityAnalytics.getCoherentQueries(
            brand_name, brand_country, brand_description, brand_industry, total_queries
        )
        
        # Save to database if session_id provided
        if convex_client and session_id:
            try:
                convex_client.save_brand_analysis(
                    session_id=session_id,
                    brand_name=brand_name,
                    brand_website=data.get('brandWebsite'),
                    brand_country=brand_country,
                    brand_description=brand_description,
                    brand_industry=brand_industry,
                    status="completed",
                    result_data={'queries': queries, 'source': 'perplexity'}
                )
                print(f"✅ Perplexity queries saved to database for session {session_id}")
            except Exception as e:
                print(f"❌ Failed to save Perplexity queries: {e}")
        
        return jsonify({'queries': queries, 'source': 'perplexity'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/perplexity-web-search', methods=['POST'])
def perplexity_web_search():
    try:
        data = request.json
        query = data.get('query')
        context = data.get('context', '')
        session_id = data.get('session_id')  # Add session_id for database saving
        
        if not query:
            return jsonify({'error': 'query is required'}), 400
        
        search_results = perplexityAnalytics.webSearchAndAnalyze(query, context)
        
        # Save to database if session_id provided
        if convex_client and session_id:
            try:
                convex_client.save_report(
                    session_id=session_id,
                    report_type="geo_analysis",
                    report_data=search_results,
                    email_sent=False,
                    recipient_email="temp@evidentia.app",  # Will be updated when email is collected
                    brand_name=data.get('brandName', 'Perplexity Search')
                )
                print(f"✅ Perplexity search results saved to database for session {session_id}")
            except Exception as e:
                print(f"❌ Failed to save Perplexity search results: {e}")
        
        return jsonify(search_results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/perplexity-brand-analysis', methods=['POST'])
def perplexity_brand_analysis():
    try:
        data = request.json
        brand_name = data.get('brandName')
        brand_website = data.get('brandWebsite')
        competitors = data.get('competitors', [])
        session_id = data.get('session_id')  # Add session_id for database saving
        
        if not brand_name or not brand_website:
            return jsonify({'error': 'brandName and brandWebsite are required'}), 400
        
        analysis_result = perplexityAnalytics.getBrandAnalysis(
            brand_name, brand_website, competitors
        )
        
        # Save to database if session_id provided
        if convex_client and session_id:
            try:
                convex_client.save_brand_analysis(
                    session_id=session_id,
                    brand_name=brand_name,
                    brand_website=brand_website,
                    competitors=competitors,
                    status="completed",
                    result_data=analysis_result
                )
                print(f"✅ Perplexity brand analysis saved to database for session {session_id}")
            except Exception as e:
                print(f"❌ Failed to save Perplexity brand analysis: {e}")
        
        return jsonify(analysis_result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stream-perplexity-search', methods=['POST'])
def stream_perplexity_search():
    data = request.json
    query = data.get('query')
    context = data.get('context', '')
    
    def generate():
        try:
            if not query:
                yield f"data: {json.dumps({'error': 'query is required'})}\n\n"
                return
            
            yield f"data: {json.dumps({'status': 'Starting Perplexity search...', 'step': 'init'})}\n\n"
            time.sleep(0.1)
            
            yield f"data: {json.dumps({'status': 'Searching web with Perplexity AI...', 'step': 'search'})}\n\n"
            search_results = perplexityAnalytics.webSearchAndAnalyze(query, context)
            
            yield f"data: {json.dumps({'status': 'Search complete!', 'step': 'complete', 'result': search_results})}\n\n"
            
        except Exception as e:
            error_msg = f"Perplexity search error: {str(e)}"
            print(f"ERROR in stream_perplexity_search: {error_msg}")
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)