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
    maxconn=20,
    host='localhost',
    port=5432,
    user='postgres',
    password=db_password,  # Use the database password from the environment variable
    dbname='magpieai_db'
)

ai21.api_key = api_key


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
                    cur.execute(
                        "INSERT INTO summaries (user_id, link, summary) VALUES (%s, %s, %s)",
                        (user_id, url, summary["summary"])
                    )
                conn.commit()
            print(summary['summary'])
            return jsonify(summary['summary']) #, success=True
        except Exception as e:
            return jsonify(message=str(e)), 500

#SIMPLIFIED SUMMARY BUTTON
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
            with connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO summaries (user_id, link, summary) VALUES (%s, %s, %s)",
                        (user_id, url, summary["summary"])
                    )
                conn.commit()
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
                                        maxTokens=7000,
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
                    summaries = [{'link': link, 'summary': summary} for link, summary in cur.fetchall()]
            return jsonify(summaries=summaries)
        except Exception as e:
            return jsonify(message=str(e)), 500


@app.route('/play-selected', methods=["POST"])
def receive_selected_text():
    if request.method == "POST":
        data = request.get_json()
        selected_text = data.get('text')
        print(selected_text)
        
        # Voice using Eleven API
        voice= "Bella"
        #voice="cloned/rodrigocl"
        # Get current timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # File name with timestamp
        nombre_archivo = f"audio{timestamp}.mp3"

        try:
            # Generate audio using Eleven API
            audio = generate(text=selected_text, voice=voice, api_key=eleven_api_key)

            # Save the audio to a file
            with open(nombre_archivo, "wb") as file:
                file.write(audio)

            with open(nombre_archivo, "rb") as file:
                audio_data = file.read()

            # Ensure to delete the audio file after sending it to the client
            #os.remove("audio.mp3")

            # Return the audio as a response
            return audio_data, 200, {'Content-Type': 'audio/mpeg'}
        except Exception as e:
            print(str(e))
            return jsonify(message='Error retrieving the audio from ElevenLabs'), 500



@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5000)

