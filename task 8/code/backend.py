import requests
from flask import Flask, render_template

app = Flask(__name__)

# NewsAPI key (signup from newsapi.org)
api_key = "1952e00232854cdd8cd4e1a5593c298c"

# Base URL
url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"

# available categories for navigation
categories = [
    'general',
    'business',
    'entertainment',
    'health',
    'science',
    'sports',
    'technology',
]

@app.route('/<category>')
def news_category(category):

    response = requests.get(url + "&category=" + category)

    if response.status_code == 200:
        news_data = response.json()

    # pass categories and current_category for navigation highlighting
    return render_template('index.html', data=news_data, categories=categories, current_category=category)


@app.route('/')
def main():

    response = requests.get(url)

    if response.status_code == 200:
        news_data = response.json()

    return render_template('index.html', data=news_data, categories=categories, current_category='general')


if __name__ == "__main__":
    app.run(debug=True)