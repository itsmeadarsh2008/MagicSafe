# app.py
from flask import Flask, render_template, request, redirect, url_for
import random
import string
import json
import os
import re

app = Flask(__name__)

URLS_FILE = 'urls.json'

def load_urls():
    if os.path.exists(URLS_FILE):
        with open(URLS_FILE, 'r') as file:
            return json.load(file)
    else:
        return {}

def save_urls(urls):
    with open(URLS_FILE, 'w') as file:
        json.dump(urls, file)

url_database = load_urls()

def generate_short_url():
    characters = string.ascii_letters + string.digits

    while True:
        short_url = ''.join(random.choice(characters) for _ in range(5))

        # Check for uniqueness
        if short_url not in url_database:
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
    url_database[short_url] = original_url
    save_urls(url_database)

    complete_short_url = url_for('redirect_to_original', short_url=short_url, _external=True)
    return render_template('index.html', short_url=complete_short_url)

@app.route('/<short_url>')
def redirect_to_original(short_url):
    original_url = url_database.get(short_url)

    if original_url:
        return redirect(original_url)
    else:
        return 'URL not found', 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)