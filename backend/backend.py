from flask import Flask, request, jsonify
from flask_cors import CORS
from psycopg2 import pool
import ai21
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os  

app = Flask(__name__)
CORS(app)

# Read the environment variables
api_key = os.getenv('AI21_API_KEY')
db_password = os.getenv('DB_PASSWORD')

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host='localhost',
    port=5432,
    user='postgres',
    password=db_password,  # Use the database password from the environment variable
    dbname='postgres'
)

ai21.api_key = api_key  # Use the API key from the environment variable


@app.route('/save-link', methods=["POST"])
def save_link():
    if request.method == "POST":
        body = request.get_json()
        url = body['url']
        user_id = body['user_id']
        with connection_pool.getconn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM user_links WHERE user_id = %s AND link = %s", (user_id, url))
                if cur.fetchone() is None:  # The link doesn't exist yet
                    cur.execute("INSERT INTO user_links (user_id, link) VALUES (%s, %s)", (user_id, url))
                    conn.commit()
                    return jsonify(success=True)
                else:
                    return jsonify(message="Link already exists"), 409


@app.route('/get-links', methods=["POST"])
def get_links():
    if request.method == "POST":
        body = request.get_json()
        user_id = body['user_id']
        with connection_pool.getconn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT link FROM user_links WHERE user_id = %s", (user_id,))
                links = [link for link, in cur.fetchall()]
        return jsonify(links=links)


@app.route('/summarize-and-save', methods=["POST"])
def summarize_and_save():
    if request.method == "POST":
        body = request.get_json()
        url = body['url']
        user_id = body['user_id']

        # Configure Chrome options
        chrome_options = Options()
        chrome_options.binary_location = os.getenv('CHROME_PATH')
        #chrome_options.add_argument('--headless')  # Run Chrome in headless mode

        # Create an instance of the Chrome driver
        driver = webdriver.Chrome(os.getenv('CHROMEDRIVER_PATH'), options=chrome_options)

        # Navigate to the URL using Selenium 
        driver.get(url)

        # Wait 10 seconds
        time.sleep(10)

        # Get the page content
        content = driver.page_source

        # Close the browser
        driver.quit()

        # Continue with the rest of the code
        soup = BeautifulSoup(content, 'html.parser')
        transcript = ' '.join(soup.stripped_strings)
        # Print the 'soup' content
        print('Soup content:')
        print(soup)

        try:
            summary = ai21.Summarize.execute(
                source=transcript,
                sourceType="TEXT"
            )
        except Exception as e:
            return (str(e), 400)
        with connection_pool.getconn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO summaries (user_id, link, summary) VALUES (%s, %s, %s)",
                    (user_id, url, summary["summary"])
                )
            conn.commit()
        return jsonify(success=True)

@app.route('/get-summaries', methods=["POST"])
def get_summaries():
    if request.method == "POST":
        body = request.get_json()
        user_id = body['user_id']
        with connection_pool.getconn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT link, summary FROM summaries WHERE user_id = %s",
                    (user_id,)
                )
                summaries = [{'link': link, 'summary': summary} for link, summary in cur.fetchall()]
        return jsonify(summaries=summaries)


if __name__ == '__main__':
    app.run(debug=True)

