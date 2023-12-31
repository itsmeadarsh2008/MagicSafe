# app.py
from flask import Flask, render_template, request, redirect, url_for
import random
import string
import os
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB Atlas
mongo_uri = os.environ.get('MONGODB_URI')  # Set your MongoDB Atlas connection URI
client = MongoClient(mongo_uri)
db = client.get_default_database()

# Create a 'urls' collection to store shortened URLs
urls_collection = db['urls']

def generate_short_url():
    characters = string.ascii_letters + string.digits

    while True:
        short_url = ''.join(random.choice(characters) for _ in range(5))

        # Check for uniqueness in MongoDB
        if not urls_collection.find_one({'short_url': short_url}):
            return short_url

def is_valid_url(url):
    # Actual regex for URL matching (starts with http:// or https://)
    return bool(re.match(r'^https?://', url))

@app.route('/')
def index():
    return render_template('index.html', short_url=None)

@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form.get('original_link')

    if not original_url or not is_valid_url(original_url):
        return render_template('index.html', short_url=None)

    short_url = generate_short_url()

    # Save the URL in MongoDB
    urls_collection.insert_one({'short_url': short_url, 'original_url': original_url})

    complete_short_url = url_for('redirect_to_original', short_url=short_url, _external=True)
    return render_template('index.html', short_url=complete_short_url)

@app.route('/<short_url>')
def redirect_to_original(short_url):
    url_document = urls_collection.find_one({'short_url': short_url})

    if url_document:
        original_url = url_document['original_url']
        return redirect(original_url)
    else:
        return 'URL not found', 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)