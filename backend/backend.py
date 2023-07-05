import re
from flask import Flask, request, jsonify
from markupsafe import escape
from flask_cors import CORS
from psycopg2 import pool
import ai21
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import os  
from dotenv import load_dotenv
# from pydantic import BaseModel, root_validator, validator
# from typing import Union, List, Optional
# from elevenlabs import clone, generate, play, set_api_key
# from elevenlabs.api import History
import requests
import datetime
load_dotenv()

app = Flask(__name__)
CORS(app)
# Constants
AUDIO_FORMAT = "audio/mp3"
# Environment variables
api_key = os.getenv('AI21_API_KEY')
db_password = os.getenv('DB_PASSWORD')
eleven_api_key = os.getenv('ELEVEN_API_KEY')
chrome_path = os.getenv('CHROME_PATH')

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=30,
    host='localhost',
    port=5432,
    user='postgres',
    password=db_password,  # Use the database password from the environment variable
    dbname='magpieai_db'
)

# Voice using Eleven API
voice= "Bella"
#voice="cloned/rodrigocl"
# Get current timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
CHUNK_SIZE = 1024
#a random voice from https://api.elevenlabs.io/v1/voices
url_voice = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"

headers = {
"Accept": "audio/mpeg",
"Content-Type": "application/json",
"xi-api-key": eleven_api_key
}

ai21.api_key = api_key

def get_website_headline(url):
    # Send a GET request to the website
    response = requests.get(url)
    
    # Create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the headline element in the HTML
    headline_element = soup.find('h1')  # Adjust this according to the specific website's HTML structure
    
    if headline_element:
        headline = headline_element.text.strip()
        headline = headline.replace(' ', '_')
        re.sub(r'[^\x00-\x7F]+','', headline)
        return headline
    else:
        return 'no_headline'

def valid_url(url):
    """valid_url
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


@app.route('/save-link', methods=["POST"])
def save_link():
    """save_link
    
    """
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
    """get_links

    Returns:
        _type_: _description_
    """
    if request.method == "POST":
        body = request.get_json()
        user_id = body['user_id']
        with connection_pool.getconn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT link FROM user_links WHERE user_id = %s", (user_id,))
                links = [link for link, in cur.fetchall()]
        return jsonify(links=links)

#SUMMARY AND SAVE OR STANDARD SUMMARY BUTTON
@app.route('/summarize-and-save', methods=["POST"])
def summarize_and_save():
    """_summary_and_save_

    Returns:
        _type_: _description_
    """
    if request.method == "POST":
        body = request.get_json()
        url = body['url']
        user_id = body['user_id']
        headline = get_website_headline(url)
        # # Configure Chrome options
        # service = Service(executable_path=r'/usr/local/bin/chromedriver')
        # chrome_options = Options()
        # chrome_options.binary_location = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" 
        # # Instantiate the Chrome Controller
        # driver = webdriver.Chrome(service=service, options=chrome_options)
        # # Navigate to url using selenium
        # driver.get(url)
        # # wait 1 seconds
        # time.sleep(1)
        # # Get the page content
        # content = driver.page_source
        # # close browser
        # driver.quit()
        # # Continue with the rest of the code
        # soup = BeautifulSoup(content, 'html.parser')
        # transcript = ' '.join(soup.stripped_strings)
        # # Print the content of 'soup'
        # print('soup content:')
        # print(soup)

        try:
            # summary = ai21.Summarize.execute(
            #     source=transcript,
            #     sourceType="TEXT"
            # )
            summary = ai21.Summarize.execute(
                source=url,
                sourceType="URL"
            ) #return a dictionary {'id', 'summary'}
        except Exception as e:
            return (str(e), 400)
        
        try:
            with connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    # Check if the URL already exists
                    cur.execute("SELECT * FROM summaries WHERE link = %s", (url,))
                    existing_row = cur.fetchone()
                    if existing_row:
                        # Delete the existing row
                        cur.execute("DELETE FROM summaries WHERE link = %s", (url,))

                    # Insert the new row
                    cur.execute(
                        "INSERT INTO summaries (user_id, link, summary) VALUES (%s, %s, %s)",
                        (user_id, url, summary["summary"])
                    )
                conn.commit()

            print(summary['summary'])

            data = {
            "text": summary['summary'],
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5}
            }

            #create audio file from Eleven API
            resp = requests.post(url_voice, json=data, headers=headers)
            print("Response status code: ", resp.status_code)
            with open(f"audio/{headline}.mp3", 'wb') as f:
                print("Writing audio file")
                # for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                #     if chunk:
                f.write(resp.content)

            return jsonify(summary['summary']) #, success=True
        
        except Exception as e:
            print(str(e))
            return jsonify(message=str(e)), 500

#SIMPLE SUMMARY BUTTON
@app.route('/simple-summary', methods=["POST"]) 
def simplified_summary():
    """simplified-summary
    query 'summaries' table for one latest summary for a given user_id, link
    generate simplified summary using Jurassic API
    
    """
    if request.method == "POST":
        body = request.get_json()
        url = body['url']
        user_id = body['user_id']
        headline = get_website_headline(url)
        #==================Web scraping==================#
        # if not valid_url(url):
        #     return jsonify(message="Invalid URL"), 400

        # # Configure Chrome options
        # chrome_options = Options()
        # chrome_options.binary_location = os.getenv('CHROME_PATH')
        # # Instantiate the Chrome Controller
        # driver = webdriver.Chrome(os.getenv('CHROMEDRIVER_PATH'), options=chrome_options)
        # # Navigate to url using selenium
        # driver.get(url)
        # # wait 10 seconds
        # time.sleep(1)
        # # Get the page content
        # content = driver.page_source
        # # close browser
        # driver.quit()
        # # Continue with the rest of the code
        # soup = BeautifulSoup(content, 'html.parser')
        # transcript = ' '.join(soup.stripped_strings)
        # # Print the content of 'soup'
        # print('soup content:')
        # print(soup)

        try:
            summary = ai21.Summarize.execute(
                source=url,
                sourceType="URL"
            )
        except Exception as e:
            return (str(e), 400)

        try:
            

            #==================After saving the summary, get the latest summary, and send to Jurassic API ==================#
            with connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT link, summary FROM summaries WHERE user_id = %s ORDER BY ID DESC LIMIT 1", #try to get the latest summary
                        (user_id,)
                    )
                    summaries = [{'link': link, 'summary': summary} for link, summary in cur.fetchall()]
                    summary = summaries[-1] #get the first element of the list

                    ## send to Jurrasic for simplified summary
                    # Read the contents of the template file
                    with open('prompt_template.txt', 'r') as file:
                        template = file.read()

                    simplified_summary = ai21.Completion.execute(
                                        model="j2-ultra",  
                                        prompt=template+summary['summary'],
                                        numResults=1,
                                        maxTokens=6000,
                                        temperature=0.4,
                                        topKReturn=0,
                                        topP=1,
                                        countPenalty={
                                            "scale": 0,
                                            "applyToNumbers": False,
                                            "applyToPunctuations": False,
                                            "applyToStopwords": False,
                                            "applyToWhitespaces": False,
                                            "applyToEmojis": False
                                        },
                                        frequencyPenalty={
                                            "scale": 0,
                                            "applyToNumbers": False,
                                            "applyToPunctuations": False,
                                            "applyToStopwords": False,
                                            "applyToWhitespaces": False,
                                            "applyToEmojis": False
                                        },
                                        presencePenalty={
                                            "scale": 0,
                                            "applyToNumbers": False,
                                            "applyToPunctuations": False,
                                            "applyToStopwords": False,
                                            "applyToWhitespaces": False,
                                            "applyToEmojis": False
                                        },  
                                        stopSequences=["Now use simplify this context:","↵↵"]
                    )
                    simplified_summary = simplified_summary['completions'][0]['data']['text']
                    print(simplified_summary+"SIMPLIFIED SUMMARY")
                    #if simplified_summary == "":

            #=========After getting the simplified summary, delete last row, save new to database ===========#
            with connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    # Check if the URL already exists
                    cur.execute("SELECT * FROM summaries WHERE link = %s", (url,))
                    existing_row = cur.fetchone()
                    if existing_row:
                        # Delete the existing row
                        cur.execute("DELETE FROM summaries WHERE link = %s", (url,))

                    # Insert the new row
                    cur.execute(
                        "INSERT INTO summaries (user_id, link, summary) VALUES (%s, %s, %s)",
                        (user_id, url, simplified_summary)
                    )
                conn.commit()

            # create audio file        
            data = {
            "text": simplified_summary,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5}
            }
            #create audio file from Eleven API
            resp = requests.post(url_voice, json=data, headers=headers)
            print("Response status code: ", resp.status_code)
            with open(f'audio/{headline}.mp3', 'wb') as f:
                print("Writing audio file")
                # for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                #     if chunk:
                f.write(resp.content)

            return jsonify(simplified_summary) 
        except Exception as e:
            return jsonify(message=str(e)), 500


#MY LIBRARY BUTTON
@app.route('/get-summaries', methods=["POST"]) 
def get_summaries():
    """get_summaries
    query summaries table for all summaries for a given user_id
    
    """
    if request.method == "POST":
        body = request.get_json()
        user_id = body['user_id']

        try:
            with connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT link, summary FROM summaries WHERE user_id = %s",
                        (user_id,)
                    )
                    summaries = [{'link': link, 'summary': summary, 'headline': get_website_headline(link)} for link, summary in cur.fetchall()]
            return jsonify(summaries=summaries)
        except Exception as e:
            return jsonify(message=str(e)), 500


@app.route('/play-selected', methods=["POST"])
def receive_selected_text():
    if request.method == "POST":
        data = request.get_json()
        selected_text = data.get('text')
        print(selected_text)
        data = {
            "text": selected_text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        try:
            #create audio file from Eleven API
            response = requests.post(url_voice, json=data, headers=headers)
            print("Response status code: ", response.status_code)
            with open('./audio/output.mp3', 'wb') as f:
                print("Writing audio file")
                # for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                #     if chunk:
                f.write(response.content)
            #output audio file
            with open('./audio/output.mp3', "rb") as file:
                audio_data = file.read()

            # Ensure to delete the audio file after sending it to the client
            #os.remove("audio.mp3")

            # Return the audio as a response
            return audio_data, 200, {'Content-Type': 'audio/mpeg'}
        except Exception as e:
            print(str(e))
            return jsonify(message='Error retrieving the audio from ElevenLabs'), 500

@app.route('/play-summary',methods=["POST"])
def play_summary():
    if request.method == "POST":
        headline = request.get_json()["headline"]
        print(headline)
        with open(f'./audio/{headline}.mp3', "rb") as file:
            audio_data = file.read()
            print("audio sent to frontend")
            return audio_data, 200, {'Content-Type': 'audio/mpeg'}

# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/refresh-db',methods=["GET"])
def refresh_all():
    if request.method == "GET":
        # body = request.get_json()
        # user_id = body['user_id']
        try:
            with connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM summaries",
                    )
                    cur.execute(
                        "DELETE FROM user_links",
                    )
            return jsonify()
        except Exception as e:
            return jsonify(message=str(e)), 500


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5000)

