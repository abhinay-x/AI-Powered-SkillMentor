"""
SkillMentor Flask Web Application
"""
import os
import uuid
import logging
from flask import Flask, request, render_template, jsonify, session
from dotenv import load_dotenv

from skillmentor.core import SkillMentor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'skillmentor-dev-key')

# Set up file paths
index_path = 'data/processed/faiss_index.bin'
documents_path = 'data/processed/documents.txt'
model_name = os.getenv('MODEL_NAME', 'meta-llama/Llama-2-7b-chat-hf')
device = os.getenv('DEVICE', 'cpu')

# Initialize SkillMentor instance
try:
    skillmentor = SkillMentor(
        index_path=index_path if os.path.exists(index_path) else None,
        documents_path=documents_path if os.path.exists(documents_path) else None,
        model_name=model_name,
        device=device
    )
    logging.info("SkillMentor instance initialized successfully")
except Exception as e:
    logging.error(f"Error initializing SkillMentor: {str(e)}")
    skillmentor = None

@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/query', methods=['GET', 'POST'])
def query():
    """Process user query and display results"""
    if request.method == 'POST':
        # Get query from form
        user_query = request.form.get('query', '')
        source_lang = request.form.get('language', 'en')
        
        if not user_query:
            return render_template('index.html', error="Please enter a query")
        
        # Generate a unique query ID
        query_id = str(uuid.uuid4())
        session['last_query_id'] = query_id
        
        try:
            # Process the query
            result = skillmentor.process_query(user_query, source_lang)
            
            # Render the results page
            return render_template(
                'result.html',
                query=result['original_query'],
                advice=result['advice_source_lang'],
                dashboard_image=result['dashboard_image'],
                response_time=f"{result['response_time']:.2f}",
                query_id=query_id
            )
        except Exception as e:
            logging.error(f"Error processing query: {str(e)}")
            return render_template('index.html', error=f"Error processing query: {str(e)}")
    
    # GET request
    return render_template('index.html')

@app.route('/feedback', methods=['POST'])
def feedback():
    """Record user feedback"""
    query_id = request.form.get('query_id')
    rating = int(request.form.get('rating', 0))
    comments = request.form.get('comments', '')
    
    if not query_id or rating < 1 or rating > 5:
        return jsonify({'success': False, 'error': 'Invalid feedback data'})
    
    try:
        # Record the feedback
        skillmentor.record_user_feedback(query_id, rating, comments)
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error recording feedback: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/metrics')
def metrics():
    """Display performance metrics"""
    try:
        metrics_data = skillmentor.get_performance_metrics()
        return render_template('metrics.html', metrics=metrics_data)
    except Exception as e:
        logging.error(f"Error getting metrics: {str(e)}")
        return jsonify({'error': str(e)})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return render_template('error.html', error="Server error"), 500

if __name__ == '__main__':
    # Check if index exists
    if not os.path.exists(index_path):
        logging.warning(f"Index file not found at {index_path}. Please run scripts/create_index.py first.")
    
    # Run the Flask app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug) 