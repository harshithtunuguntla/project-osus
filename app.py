from bson import ObjectId
from flask import Flask, render_template, request, jsonify, redirect
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
client = MongoClient(os.getenv('MONGO_PATH'), int(os.getenv('MONGO_PORT')))

# MongoDB Database Access
database = client.ShortUrlDatabase
ShortUrlDatabase = database.URLData

def is_keyword_present(keyword):
    """Check if the keyword is already present in the database"""
    return ShortUrlDatabase.count_documents({'keyword': keyword}) > 0
@app.route('/')
def home():
    '''
    Index page for URL Shortener (Project OSUS (Open Source URL Shortener))
    '''
    print('Home Page API Called, rendering template')
    return render_template('index.html')
@app.route('/shorten', methods=['POST'])
def shortenAPI():
    '''
    This method will shorten the link and give the short URL
    '''
    print('URL Shorten Called')
    print('Mongo Connection: ' + str(os.getenv('MONGO_PATH')[:6]))

    if request.method == 'POST':
        longUrl = request.json.get("longUrl")
        keyword = request.json.get("keyword")

        # Logs
        print('Long URL Received: ' + str(longUrl))
        print('Keyword Received: ' + str(keyword))

        # If no keyword is provided, use MongoDB's _id as the short URL
        if not keyword:
            # Insert the long URL into the DB and get the inserted document's _id
            inserted_document = ShortUrlDatabase.insert_one({'url': longUrl, 'clicks': 0})
            keyword = str(inserted_document.inserted_id)
            print('No keyword provided, using MongoDB _id: ' + keyword)
        else:
            # If keyword exists, return an error
            if is_keyword_present(keyword):
                print('Keyword is present, throwing error')
                return jsonify({'error': 'The Keyword Already Exists, Choose a Different One'}), 400
            
            # Insert with the provided keyword
            ShortUrlDatabase.insert_one({'keyword': keyword, 'url': longUrl, 'clicks': 0})
            print('DB insert successful with provided keyword')

        # Return the short URL with either the keyword or MongoDB's _id
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
    link_status = 0
    print('Finding the URL Keyword')
    print('Mongo Connection: '+str(os.getenv('MONGO_PATH')[:6]))
    item = ShortUrlDatabase.find_one({'$or': [{'keyword': keyword}, {'_id': ObjectId(keyword)}]})
    if item:
        redirection = item['url']
        # Write Logs Here
        print('Short URL <> Long URL mapping found in DB')
        link_status = 1
    if (link_status == 0):
        print('Link Not Found in DB')
        return "Link Not Found"
    print('Redirecting to long url: '+str(redirection))
    return redirect(redirection, code=302)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
