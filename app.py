
from flask import Flask, render_template, request, jsonify, redirect
from pymongo import MongoClient
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import os
import random
import string

load_dotenv()

app = Flask(__name__)

# MongoDB Setup
client = MongoClient(os.getenv('MONGO_PATH'), int(os.getenv('MONGO_PORT')))
db = client.ShortUrlDatabase
url_collection = db.URLData

# Helper Functions
def generate_random_string(length=5):
    """Generate a random string of specified length with both uppercase and lowercase letters."""
    return ''.join(random.choices(string.ascii_letters, k=length))

def check_keyword_existence(keyword):
    """Check if the given keyword already exists in the database."""
    return url_collection.find_one({'keyword': keyword}) is not None

def insert_url_data(keyword, long_url, metadata=None):
    """Insert the long URL, keyword, and metadata (if available) into the database."""
    url_collection.insert_one({
        'keyword': keyword,
        'url': long_url,
        'clicks': 0,
        'metadata': metadata or {}
    })

def get_long_url_by_keyword(keyword):
    """Retrieve the long URL and metadata associated with the given keyword."""
    return url_collection.find_one({'keyword': keyword})

def update_click_count(keyword):
    """Increment the click count for the given keyword."""
    url_collection.update_one({'keyword': keyword}, {'$inc': {'clicks': 1}})

def fetch_url_metadata(url):
    """Fetch metadata like title, description, and image from the given URL."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').get_text() if soup.find('title') else 'No title'
        description = soup.find('meta', attrs={'name': 'description'})
        description = description['content'] if description else 'No description available'
        image = soup.find('meta', property='og:image') or soup.find('meta', attrs={'name': 'image'})
        image = image['content'] if image else ''

        return {
            'title': title,
            'description': description,
            'image': image
        }
    except Exception as e:
        return {'error': str(e)}

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
    """Shorten the given long URL and return a short URL with metadata if available."""
    if request.method == 'POST':
        long_url = request.json.get("longUrl")
        keyword = request.json.get("keyword", '')

        if not long_url:
            return jsonify({'error': 'Long URL is required'}), 400
        
        if not keyword:
            keyword = generate_random_string()

        if check_keyword_existence(keyword):
            return jsonify({'error': 'The keyword already exists. Please choose a different one.'}), 400

        # Fetch metadata for the link preview
        metadata = fetch_url_metadata(long_url)

        # Insert URL data along with metadata
        insert_url_data(keyword, long_url, metadata)

        short_url = f'{request.host_url}{keyword}'
        return jsonify({
            'shortUrl': short_url,
            'metadata': metadata  # Return metadata in response
        }), 200

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
