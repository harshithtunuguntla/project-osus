from flask import Flask, render_template, request, jsonify, redirect
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import random
import string
import uuid

load_dotenv()

app = Flask(__name__)

# MongoDB Setup
client = MongoClient(os.getenv('MONGO_PATH'), int(os.getenv('MONGO_PORT')))
db = client.ShortUrlDatabase
url_collection = db.URLData

# Helper Functions
def generate_random_string():
    """
    Generates a random string using UUID of length 36.

    Returns:
        str: A random UUID string.
    """
    return str(uuid.uuid4())

def check_keyword_existence(keyword):
    """Check if the given keyword already exists in the database."""
    return url_collection.find_one({'keyword': keyword}) is not None

def insert_url_data(keyword, long_url):
    """Insert the long URL and keyword into the database."""
    url_collection.insert_one({
        'keyword': keyword,
        'url': long_url,
        'clicks': 0
    })

def get_long_url_by_keyword(keyword):
    """Retrieve the long URL associated with the given keyword."""
    return url_collection.find_one({'keyword': keyword})

def update_click_count(keyword):
    """Increment the click count for the given keyword."""
    url_collection.update_one({'keyword': keyword}, {'$inc': {'clicks': 1}})

# Routes
@app.route('/')
def home():
    """Render the index page."""
    return render_template('index.html')

@app.route('/documentation')
def documentation():
    """Render the documentation page."""
    return render_template('documentation.html')

@app.route('/getURL')
def current_url():
    """Return the current working URL of the application."""
    return f'The app is running on {request.host_url}'

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """Shorten the given long URL and return a short URL."""
    if request.method == 'POST':
        long_url = request.json.get("longUrl")
        keyword = request.json.get("keyword", '')

        if not long_url:
            return jsonify({'error': 'Long URL is required'}), 400
        
        if not keyword:
            keyword = generate_random_string()
            max_attempts = 5
            attempts = 0
            while check_keyword_existence(keyword) and attempts < max_attempts:
                keyword = generate_random_string()
                attempts += 1
                
            if attempts == max_attempts:
                return jsonify({'error': 'Failed to generate a unique keyword. Please try again.'}), 500

        if check_keyword_existence(keyword):
            return jsonify({'error': 'The keyword already exists. Please choose a different one.'}), 400
        
        insert_url_data(keyword, long_url)
        short_url = f'{request.host_url}{keyword}'
        return jsonify({'shortUrl': short_url}), 200

@app.route('/analytics', methods=['GET', 'POST'])
def analytics():
    """Return analytics data for a shortened URL."""
    if request.method == 'GET':
        return render_template('analytics.html')

    if request.method == 'POST':
        keyword = request.json.get("keyword")
        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400
        
        url_data = get_long_url_by_keyword(keyword)
        if not url_data:
            return jsonify({'error': 'Keyword not found.'}), 404
        
        return jsonify({'clicks': url_data['clicks']}), 200

@app.route('/heartbeat')
def heartbeat():
    """Check if the website is running."""
    return 'The website is up'

@app.route('/<keyword>')
def redirect_to_long_url(keyword):
    """Redirect to the long URL associated with the given keyword."""
    url_data = get_long_url_by_keyword(keyword)
    
    if not url_data:
        return render_template('errorpage.html')
    
    update_click_count(keyword)
    return redirect(url_data['url'], code=302)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
