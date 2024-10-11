from bson import ObjectId
from flask import Flask, render_template, request, jsonify, redirect
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import string
load_dotenv()

app = Flask(__name__)
client = MongoClient(os.getenv('MONGO_PATH'), int(os.getenv('MONGO_PORT')))

# MongoDB Database Access
database = client.ShortUrlDatabase
ShortUrlDatabase = database.URLData

# Define the base characters (0-9, a-z)
chars = string.digits + string.ascii_lowercase
base = len(chars)

# Helper function to convert string to a base 36-like number
def str_to_num(s):
    num = 0
    for char in s:
        num = num * base + chars.index(char)
    return num

# Helper function to convert a number back to base 36-like string
def num_to_str(num, length):
    s = ""
    while num > 0:
        s = chars[num % base] + s
        num //= base
    # Pad the result with leading zeroes if needed
    return s.rjust(length, '0')

# Function to increment the custom alphanumeric string
def increment_string(s):
    num = str_to_num(s)  # Convert string to number
    incremented_num = num + 1  # Add 1 to the number
    return num_to_str(incremented_num, len(s))  # Convert back to string with the same length

def is_keyword_present(keyword):
    """Check if the keyword is already present in the database"""
    return ShortUrlDatabase.count_documents({'keyword': keyword}) > 0

def get_last_short_code():
    """Get the last short code stored in the database for incrementation"""
    last_entry = ShortUrlDatabase.find_one(sort=[('_id', -1)])
    if last_entry and 'short' in last_entry:
        return last_entry['short']
    else:
        return '0000'  # Start from '0000' if no previous short code exists

@app.route('/')
def home():
    '''
    Index page for URL Shortener (Project OSUS - Open Source URL Shortener)
    '''
    print('Home Page API Called, rendering template')
    return render_template('index.html')
@app.route('/shorten', methods=['POST'])
def shortenAPI():
    '''
    This method will shorten the link and give the short URL.
    '''
    print('URL Shorten Called')
    print('Mongo Connection: ' + str(os.getenv('MONGO_PATH')[:6]))

    if request.method == 'POST':
        longUrl = request.json.get("longUrl")
        keyword = request.json.get("keyword")

        # Logs
        print('Long URL Received: ' + str(longUrl))
        print('Keyword Received: ' + str(keyword))

        # Check if the long URL already exists
        existing_entry = ShortUrlDatabase.find_one({'url': longUrl})
        if existing_entry:
            # Return the existing short URL if the long URL is already present
            existing_short_code = existing_entry.get('short') or existing_entry.get('keyword')
            if existing_short_code:  # Ensure it's not None
                existing_short_url = str(request.host_url) + existing_short_code
                print(f'Long URL already exists. Returning existing short URL: {existing_short_url}')
                return jsonify({'shortUrl': existing_short_url})
            else:
                print('Existing entry found, but no short URL or keyword available.')
                return jsonify({'error': 'Short URL not found in existing entry.'}), 404

        # If no keyword is provided, generate an incremented short URL
        if not keyword:
            # Get the last short code from the database and increment it
            last_short_code = get_last_short_code()
            new_short_code = increment_string(last_short_code)

            # Insert the long URL into the DB with the new short code
            ShortUrlDatabase.insert_one({'url': longUrl, 'short': new_short_code, 'clicks': 0})
            keyword = new_short_code
            print(f'No keyword provided, generated short URL: {keyword}')
        else:
            # If keyword exists, return an error
            if is_keyword_present(keyword):
                print('Keyword is present, throwing error')
                return jsonify({'error': 'The Keyword Already Exists, Choose a Different One'}), 400

            # Insert with the provided keyword
            ShortUrlDatabase.insert_one({'keyword': keyword, 'url': longUrl, 'clicks': 0})
            print('DB insert successful with provided keyword')

        # Return the short URL with either the keyword or the generated short code
        return jsonify({'shortUrl': str(request.host_url) + str(keyword)})

    if request.method == 'GET':
        print('Called GET method on shorten end-point, throwing error')
        return "GET Method Not Allowed On This End Point", 405
@app.route('/analytics', methods=['GET', 'POST'])
def analyticsAPI():
    # No Authentication to check the analytics of the URL as of now
    '''
    This end point will take URL and will provide the analytics for that URL, since we don\'t have authentication we\'ll be asking just for the keyword and we\'ll give the analytics for the URL as of now '''
    print('Analytics API Called')
    return 'Under Development'

@app.route('/heartbeat')
def hearBeat():
    '''
    This end point should do all the checks/ add dummy data to DB if required and respond saying the website is UP
    '''
    print('heartbeat API called')
    return 'The website is up'
@app.route('/<keyword>')
def reroute(keyword):
    print('Clicked on shortURL')
    print('Finding the URL for Keyword: ' + str(keyword))
    print('Mongo Connection: ' + str(os.getenv('MONGO_PATH')[:6]))

    # Check if the keyword exists in the database
    item = ShortUrlDatabase.find_one({'$or': [{'keyword': keyword}, {'short': keyword}]})

    if item:
        redirection = item['url']
        print(f'Short URL <> Long URL mapping found in DB, redirecting to {redirection}')
        
        # Increment the clicks count for this URL
        ShortUrlDatabase.update_one({'$or': [{'keyword': keyword}, {'short': keyword}]}, {'$inc': {'clicks': 1}})
        
        return redirect(redirection, code=302)

    print('Link Not Found in DB')
    return "Link Not Found", 404
if __name__ == '__main__':
    app.run(debug=True, port=5000)
