from flask import Flask, render_template, request, jsonify, redirect
from datetime import datetime
from pytz import timezone, utc
import os
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import random
import string
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)

# MongoDB Setup
client = MongoClient(os.getenv('MONGO_PATH'), int(os.getenv('MONGO_PORT')))
#For Mongo atlas 
#mongo_uri = os.getenv('MONGO_PATH')
#client = MongoClient(mongo_uri)
# MongoDB Database Access
database = client.ShortUrlDatabase
ShortUrlDatabase = database.URLData

# Helper Functions
def generate_random_string(length=5):
    """Generate a random string of specified length with both uppercase and lowercase letters."""
    return ''.join(random.choices(string.ascii_letters, k=length))

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
def currentURl():
    '''
    This function will return the current working URL, something like 'http://127.0.0.1:5000/'
    '''
    print('getURL API Called')
    current_url = request.host_url
    print('Current URL: '+str(current_url))
    return f'The app is running on {current_url}'


@app.route('/shorten', methods=['POST'])
def shortenAPI():
    '''
    This method will shorten the link and give the short URL
    '''
    print('URL Shorten Called')
    print('Mongo Connection: '+str(os.getenv('MONGO_PATH')[:6]))
    
    if request.method == 'POST':
        longUrl = request.json.get("longUrl")
        keyword = request.json.get("keyword")

        # Logs
        print('Long URL Received: ' + str(longUrl))
        print('Keyword Received: ' + str(keyword))

        if keyword == '':
            keyword = generate_random_string()
            print('New keyword generated: ' + str(keyword))
        
        # Prepare the data to insert
        url_data = {
            'keyword': keyword,
            'url': longUrl,
            'clicks': 0
        }

        # Check if the keyword is already present
        if is_keyword_present(keyword) == 0:
            print('Keyword is not present, inserting into DB')
            print('Data to be inserted:', url_data)  # Print the data being inserted
            ShortUrlDatabase.insert_one(url_data)
            print('DB insert successful')
        else:
            print('Keyword is present, throwing error')
            return jsonify({'error': 'The keyword already exists. Please choose a different one.'}), 400

    if request.method == 'GET':
        print('Called get method on shorten end-point, throwing error')
        return "GET Method Not Allowed On This End Point"

    return jsonify({'shortUrl': str(request.host_url) + str(keyword)})


@app.route('/analytics', methods=['GET', 'POST'])
def analyticsAPI():
    '''
This /analytics route consists of both GET and POST requests.
- GET: Returns the analytics.html file.
- POST: Returns the total number of clicks (visits) for the specific shortened URL from the DB.
'''

    if request.method == 'GET':
        # Serve the analytics.html template for GET requests
        print('Analytics page requested.')
        return render_template('analytics.html')

    if request.method == 'POST':
        keyword = request.json.get("keyword")
        print('Keyword Received: ' + str(keyword))

        # Check if the keyword exists in the database
        url_data = ShortUrlDatabase.find_one({'keyword': keyword})

        if url_data:
            # Return the current clicks count without incrementing
            clicks_count = url_data['clicks']
            print(f'Keyword: {keyword}, Clicks Count: {clicks_count}')
            return jsonify({'clicks': clicks_count}), 200
        else:
            print('Keyword not found in DB')
            return jsonify({'error': 'Keyword not found.'}), 404




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
    app.run(host='0.0.0.0', port=5000)
