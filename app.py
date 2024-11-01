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
web_traffic_collection = db.WebTraffic

# Helper Functions
def update_click_count(keyword):
    """Increment the click count for the given keyword."""
    web_traffic_collection.update_one({'keyword': keyword}, {'$inc': {'clicks': 1}})
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
from pymongo import MongoClient


# Function to increment the visitor count in the WebTraffic collection
def increment_visitor_count():
    """Increment the visitor count."""
    web_traffic_collection.update_one(
        {},  # Update all documents (or you can use a specific filter)
        {'$inc': {'visitors': 1}}  # Increment the visitors field
    )

# Function to retrieve the visitor count
def get_visitor_count():
    """Retrieve the visitor count from the WebTraffic collection."""
    result = web_traffic_collection.find_one({}, {'visitors': 1})  # Retrieve only the visitors field
    return result['visitors'] if result and 'visitors' in result else 0

# Function to increment the 'links_Generated' count
def update_links_generated():
    """Increment the links generated count."""
    web_traffic_collection.update_one(
        {},  # Update all documents (or you can use a specific filter)
        {'$inc': {'links_Generated': 1}}  # Increment the links_Generated field
    )

# Function to get the current 'links_Generated' count
def get_links_count():
    """Get the current links generated count."""
    result = web_traffic_collection.find_one({}, {'links_Generated': 1})  # Retrieve only the links_Generated field
    return result['links_Generated'] if result and 'links_Generated' in result else 0


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

@app.route('/')
def home():
    """Render the index page with visitor count and links count."""
    increment_visitor_count()  # Increment the visitor count each time the home page is accessed
    
    visitor_count = get_visitor_count()  # Get the current visitor count
    links_count = get_links_count()  # Get the count of links generated

    return render_template('index.html', visitor_count=visitor_count, links_count=links_count)  # Pass both counts to the template

@app.route('/documentation')
def documentation():
    """Render the documentation page."""
    increment_visitor_count()  # Increment the Interations count

    return render_template('documentation.html')
@app.route('/api-docs')
def api_documentation():
    """Render the api docs page."""
    increment_visitor_count()  # Increment the Interations count

    return render_template('api.html')

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
            increment_visitor_count()  # Increment the Interations count
    
            return jsonify({'error': 'The keyword already exists. Please choose a different one.'}), 400
        insert_url_data(keyword, longUrl,expiration_datetime_utc)
        short_url = f'{request.host_url}{keyword}'
        # Update the links generated count
        update_links_generated()
        increment_visitor_count()  # Increment the Interations count
    

        # Get the updated counts
        current_links_generated = get_links_count()  # Assume this function retrieves the count
        current_visitors_count = get_visitor_count()  # Function to get the current visitors count

        # Create the short URL
        short_url = f'{request.host_url}{keyword}'

        # Return the response with short URL, keyword, and counts
        return jsonify({
            'shortUrl': short_url,
            'linksGenerated': current_links_generated,
            'visitorsCount': current_visitors_count  # Include visitors count
        }), 200

@app.route('/analytics', methods=['GET', 'POST'])
def analyticsAPI():
    '''
    This /analytics route consists of both GET and POST requests.
    - GET: Returns the analytics.html file.
    - POST: Returns the total number of clicks (visits) for the specific shortened URL from the DB along with expiration details if applicable.
    '''

    if request.method == 'GET':
        print('Analytics page requested.')
        increment_visitor_count()  # Increment the Interations count

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
            increment_visitor_count()  # Increment the Interations count

            return jsonify(response_data), 200
        else:
            print('Keyword not found in DB')
            increment_visitor_count()  # Increment the Interations count
    
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
        increment_visitor_count()  # Increment the Interations count

        return render_template('errorpage.html', 
                               title="Oops! Page Not Found", 
                               message="404 - The URL you are trying to reach doesn't exist!")

    utc = pytz.utc 
    current_time = datetime.now(utc)  # Get current time in UTC

    expiration_time = url_data.get('expiration')  # Use .get() to avoid KeyError
    if expiration_time is None:
        update_click_count(keyword)
        increment_visitor_count()  # Increment the Interations count
    
        return redirect(url_data['url'], code=302)

    # If expiration_time is present, perform the comparison
    unix_current_time = current_time.timestamp()
    unix_expiration_time = expiration_time.timestamp()

    if unix_current_time > unix_expiration_time:
        increment_visitor_count()  # Increment the Interations count
    
        return render_template('errorpage.html', 
                               title="Oops! URL has expired", 
                               message="404 - The URL you are trying to reach has expired!")

    update_click_count(keyword)
    increment_visitor_count()  # Increment the Interations count

    return redirect(url_data['url'], code=302)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
