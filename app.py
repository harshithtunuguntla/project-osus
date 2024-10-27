from flask import Flask, render_template, request, jsonify, redirect
from datetime import datetime 
import pytz

from pytz import timezone, utc
import os
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
import random
import string

load_dotenv()


app = Flask(__name__)

# MongoDB Setup
client = MongoClient(os.getenv('MONGO_PATH'),int(os.getenv('MONGO_PORT')))
db = client.ShortUrlDatabase
url_collection = db.URLData

# Helper Functions
def generate_random_string(length=5):
    """Generate a random string of specified length with both uppercase and lowercase letters."""
    return ''.join(random.choices(string.ascii_letters, k=length))

def check_keyword_existence(keyword):
    """Check if the given keyword already exists in the database."""
    return url_collection.find_one({'keyword': keyword}) is not None

def insert_url_data(keyword, longUrl, expiration_datetime_utc ):
    """Insert the long URL and keyword into the database."""
    url_collection.insert_one( {
            'keyword': keyword,
            'url': longUrl,
            'clicks': 0,
            'created_at': datetime.now(timezone.utc),
            'expiration': expiration_datetime_utc  # This will be None if no expiration is set
        })

def get_long_url_by_keyword(keyword):
    """Retrieve the long URL associated with the given keyword."""
    return url_collection.find_one({'keyword': keyword})

def update_click_count(keyword):
    """Increment the click count for the given keyword."""
    url_collection.update_one({'keyword': keyword}, {'$inc': {'clicks': 1}})
from datetime import datetime

def get_expiration_datetime(expiration_date, expiration_time, expiration_period=None, user_timezone=None):
    expiration_datetime_utc = None
    print(expiration_period)

    if expiration_date and expiration_time:
        # Normalize the expiration_time if it contains "PM" and is in 24-hour format
        if expiration_period and expiration_period.upper() == 'PM' and int(expiration_time.split(':')[0]) > 12:
            # Convert 24-hour PM time to 12-hour format
            hour = int(expiration_time.split(':')[0]) - 12
            expiration_time = f"{hour}:{expiration_time.split(':')[1]}"

        # Create the datetime string
        expiration_datetime_str = f"{expiration_date} {expiration_time} {expiration_period.upper() if expiration_period else ''}".strip()
        print(expiration_datetime_str)

        try:
            # Parse the datetime as per the provided format
            if expiration_period and expiration_period.upper() in ['AM', 'PM']:
                # Parse as 12-hour format with AM/PM
                expiration_datetime = datetime.strptime(expiration_datetime_str, '%Y-%m-%d %I:%M %p')
            else:
                # Parse as 24-hour format (no AM/PM)
                expiration_datetime = datetime.strptime(expiration_datetime_str, '%Y-%m-%d %H:%M')

            # If a timezone is provided, localize the datetime to that timezone
            if user_timezone:
                local_tz = pytz.timezone(user_timezone)
                local_expiration_dt = local_tz.localize(expiration_datetime)
                # Convert local datetime to UTC
                expiration_datetime_utc = local_expiration_dt.astimezone(pytz.utc)
            else:
                # If no timezone is provided, treat the datetime as UTC
                expiration_datetime_utc = expiration_datetime

            return expiration_datetime_utc
        except ValueError:
            return {'error': 'Invalid expiration time format. Use HH:MM AM/PM for 12-hour or HH:MM for 24-hour format.'}, 400
    return None  # Return None if no expiration is set

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
def shortenAPI():
    '''
    This method will shorten the link and give the short URL with an optional expiration time.
    '''
    print('URL Shorten Called')
    print('Mongo Connection: ' + str(os.getenv('MONGO_PATH')[:6]))
    print("Called")

    if request.method == 'POST':
        # Extracting data from the request
        longUrl = request.json.get("longUrl")
        keyword = request.json.get("keyword")
        expiration_date = request.json.get("expirationDate")  # Date in 'YYYY-MM-DD' format (optional)
        expiration_time = request.json.get("expirationTime")  # Time in 'HH:MM' format (optional)
        expiration_period = request.json.get("expirationPeriod")  # 'AM' or 'PM' (optional)
        user_timezone = request.json.get("timezone")  # User's timezone (optional)

        # Logs
        print('Long URL Received: ' + str(longUrl))
        print('Keyword Received: ' + str(keyword))

        # Generate a random keyword if none provided
        if not keyword or keyword == '':
            keyword = generate_random_string()

        # Combine expiration date and time if provided
        expiration_datetime_utc=get_expiration_datetime(expiration_date,expiration_time,expiration_period,user_timezone)
      
        # Check if the keyword is already present in the database
        if check_keyword_existence(keyword):
            return jsonify({'error': 'The keyword already exists. Please choose a different one.'}), 400
        insert_url_data(keyword, longUrl,expiration_datetime_utc)
        short_url = f'{request.host_url}{keyword}'
        return jsonify({'shortUrl': short_url}), 200

@app.route('/analytics', methods=['GET', 'POST'])
def analyticsAPI():
    '''
    This /analytics route consists of both GET and POST requests.
    - GET: Returns the analytics.html file.
    - POST: Returns the total number of clicks (visits) for the specific shortened URL from the DB along with expiration details if applicable.
    '''

    if request.method == 'GET':
        print('Analytics page requested.')
        return render_template('analytics.html')

    if request.method == 'POST':
        keyword = request.json.get("keyword")
        print('Keyword Received: ' + str(keyword))

        # Check if the keyword exists in the database
        url_data = url_collection.find_one({'keyword': keyword})

        if url_data:
            # Return the current clicks count and expiration details
            clicks_count = url_data['clicks']
            expiration = url_data.get('expiration')

            response_data = {'clicks': clicks_count}

            if expiration:
                remaining_time = handle_expiration(expiration)
                response_data['expiration'] = remaining_time
            
            print(f'Keyword: {keyword}, Clicks Count: {clicks_count}, Expiration: {response_data.get("expiration")}')
            return jsonify(response_data), 200
        else:
            print('Keyword not found in DB')
            return jsonify({'error': 'Keyword not found.'}), 404

def handle_expiration(expiration):
    # Return the entire expiration timestamp as a string
    return expiration.isoformat()  # Returns in ISO 8601 format (YYYY-MM-DDTHH:MM:SS.mmmmmm)



@app.route('/heartbeat')
def heartbeat():
    """Check if the website is running."""
    return 'The website is up'

@app.route('/<keyword>')
def redirect_to_long_url(keyword):
    """Redirect to the long URL associated with the given keyword."""
    url_data = get_long_url_by_keyword(keyword)

    if not url_data:
        return render_template('errorpage.html', 
                               title="Oops! Page Not Found", 
                               message="404 - The URL you are trying to reach doesn't exist!")

    utc = pytz.utc 
    current_time = datetime.now(utc)  # Get current time in UTC

    expiration_time = url_data.get('expiration')  # Use .get() to avoid KeyError
    if expiration_time is None:
        return redirect(url_data['url'], code=302)

    # If expiration_time is present, perform the comparison
    unix_current_time = current_time.timestamp()
    unix_expiration_time = expiration_time.timestamp()

    if unix_current_time > unix_expiration_time:
        return render_template('errorpage.html', 
                               title="Oops! URL has expired", 
                               message="404 - The URL you are trying to reach has expired!")

    update_click_count(keyword)
    return redirect(url_data['url'], code=302)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
