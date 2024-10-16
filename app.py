from flask import Flask, render_template, request, jsonify, redirect
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import random
import string

load_dotenv()

app = Flask(__name__)
# Use the connection string from the .env file
#client = MongoClient(os.getenv('MONGO_PATH'), int(os.getenv('MONGO_PORT')))
#For Mongo atlas 
mongo_uri = os.getenv('MONGO_PATH')
client = MongoClient(mongo_uri)
# MongoDB Database Access
database = client.ShortUrlDatabase
ShortUrlDatabase = database.URLData


# Functions
def generate_random_string(length=5):
    '''
    This function gives a combination of lowercase and uppercase letters of k length
    '''
    print('generating a random keyword')
    letters = string.ascii_letters
    random_string = ''.join(random.choices(letters, k=length))
    print('keyword generated: '+str(random_string))
    return random_string


def is_keyword_present(keyword):
    '''
    Function to check if the current keyword is present in the DB or not
    '''
    print('Fetching if keyword is present in DB: '+str(keyword))
    present = 0
    for item in ShortUrlDatabase.find():
        if (item['keyword'] == keyword):
            print('keyword present in DB: '+str(keyword))
            present = 1
    print('keyword not present in DB: '+str(keyword))
    return present

# Routes


@app.route('/')
def home():
    '''
    Index page for URL Shortener (Project OSUS (Open Source URL Shortener))
    '''
    print('Home Page API Called, rendering template')
    return render_template('index.html')

@app.route('/documentation')
def documentation():          
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
def hearBeat():
    '''
    This end point should do all the checks/ add dummy data to DB if required and respond saying the website is UP
    '''
    print('heartbeat API called')
    return 'The website is up'

@app.route('/<keyword>')
def reroute(keyword):
    print('Clicked on shortURL')
    link_status = 0
    redirection = None  # Initialize redirection variable
    print('Finding the URL Keyword')
    print('Mongo Connection: ' + str(os.getenv('MONGO_PATH')[:6]))
    
    # Find the URL associated with the keyword
    for item in ShortUrlDatabase.find():
        if item['keyword'] == keyword:
            redirection = item['url']
            # Increment the clicks count
            ShortUrlDatabase.update_one(
                {'keyword': keyword}, 
                {'$inc': {'clicks': 1}}  # Increment clicks by 1
            )
            print('Short URL <> Long URL mapping found in DB')
            link_status = 1
            break  # Break out of the loop once the keyword is found

    if link_status == 0:
        print('Link Not Found in DB')
        return render_template('errorpage.html')
    
    print('Redirecting to long URL: ' + str(redirection))
    return redirect(redirection, code=302)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
