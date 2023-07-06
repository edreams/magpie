import re
import json
from flask import Flask, request, jsonify
from markupsafe import escape
from flask_cors import CORS
from psycopg2 import pool
import ai21
import requests
from bs4 import BeautifulSoup
import time
import os  
from dotenv import load_dotenv
from elevenlabs import generate
import requests
import datetime
from urllib.parse import urlparse
from flask import Flask, render_template
load_dotenv()

app = Flask(__name__)
CORS(app)
print(os.getcwd())
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
    dbname='magpieai_db5'
)

def create_connection():
    connection = connection_pool.getconn()
    return connection

@app.route('/create-user', methods=['POST'])
def create_user():
    data = request.get_json()
    user_id = data.get('user_id')
    print(user_id)
    if not user_id:
        return jsonify({'error': 'User ID is required.'}), 400

    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Verificar si el usuario ya existe
        query = "SELECT * FROM users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({'error': 'User already exists.'}), 409

        # Crear un nuevo usuario
        query = "INSERT INTO users (user_id) VALUES (%s) RETURNING user_id"
        cursor.execute(query, (user_id,))
        new_user_id = cursor.fetchone()[0]

        connection.commit()

        return jsonify({'user_id': new_user_id}), 200

    except (Exception, connection.Error) as error:
        return jsonify({'error': 'Error creating user.'}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection_pool.putconn(connection)
            
            
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
        user_id_json = json.loads(body['user_id'])  # parse the JSON string
        user_id = user_id_json['user_id']  # get the value of user_id
        print("user_id")
        print(user_id)
        print(type(user_id))
        headline = get_website_headline(url)
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
        user_id_json = json.loads(body['user_id'])  # parse the JSON string
        user_id = user_id_json['user_id']  # get the value of user_id
        print("user_id")
        print(user_id)
        print(type(user_id))
        
        with connection_pool.getconn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT link FROM user_links WHERE user_id = %s", (user_id,))
                links = [link for link, in cur.fetchall()]
        return jsonify(links=links)

#SUMMARY AND SAVE OR STANDARD SUMMARY BUTTON
@app.route('/summarize-and-save', methods=["POST"])
def summarize_and_save():
    if request.method == "POST":
        body = request.get_json()
        url = body['url']
        user_id_json = json.loads(body['user_id'])
        user_id = user_id_json['user_id']
        content = body['content']

        with connection_pool.getconn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM user_links WHERE user_id = %s AND link = %s",
                    (user_id, url)
                )
                existing_link = cur.fetchone()

                if not existing_link:
                    cur.execute(
                        "INSERT INTO user_links (user_id, link) VALUES (%s, %s)",
                        (user_id, url)
                    )
                    conn.commit()
                else: 
                    print("existing_link")
                    print(existing_link)
                    cur.execute(
                        "SELECT summary FROM summaries WHERE user_id = %s AND type = 'standard'",
                        (existing_link[0],)
                    )
                    summary = cur.fetchone()

                    if summary:
                        return jsonify(summary), 200
                    else:
                        return jsonify(message="No se encontró el resumen correspondiente al enlace y usuario."), 404

        headline = get_website_headline(url)
        print(headline)
        try:
            summary = ai21.Summarize.execute(
                 source=content,
                 sourceType="TEXT"
             )
            print("existing_link")
            print(existing_link)
        except Exception as e:
            return (str(e), 400)
        
        try:
            with connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO summaries (user_id, link, type, summary, audio) VALUES (%s, %s, %s, %s, %s)",
                        (user_id, url, 'standard', summary["summary"], None)
                    )
                    conn.commit()

            try:
                print(summary)
                print(summary["summary"])
                return jsonify(summary["summary"]) 
            except Exception as e:
                return jsonify(message='Error retrieving the audio'), 500
        
        except Exception as e:
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
        user_id_json = json.loads(body['user_id'])  # parse the JSON string
        user_id = user_id_json['user_id']  # get the value of user_id
        transcript = body['content']
        print("transcript")
        print(transcript)

        print("user_id")
        print(user_id)
        print(type(user_id))
        headline = get_website_headline(url)
                # Verificar si el enlace ya existe para el usuario actual
        with connection_pool.getconn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM user_links WHERE user_id = %s AND link = %s",
                    (user_id, url)
                )
                existing_link = cur.fetchone()

                if not existing_link:
                    # Si el enlace no existe, lo creamos
                    cur.execute(
                        "INSERT INTO user_links (user_id, link) VALUES (%s, %s)",
                        (user_id, url)
                    )
                    conn.commit()
                


        try:
            summary = ai21.Summarize.execute(
                source=transcript,
                sourceType="TEXT"
            )
        except Exception as e:
            return (str(e), 400)

        try:
            with connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    # cur.execute(
                    #     "INSERT INTO summaries (user_id, link, summary) VALUES (%s, %s, %s)",
                    #     (user_id, url, summary["summary"])
                    cur.execute(
                        "INSERT INTO summaries (user_id, link, type, summary, audio) VALUES (%s, %s, %s, %s, %s)",
                        (user_id, url, 'simple', summary["summary"], None)
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
                                        maxTokens=4000,
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

            #print(simplified_summary)


            try:
                #audio_data, status_code, headers = generate_audio(headline+"_simple", simplified_summary)
                return jsonify(simplified_summary) 
            except Exception as e:
                print(str(e))
                return jsonify(message='Error retrieving the audio from ElevenLabs'), 500
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
        user_id_json = json.loads(body['user_id'])  # parse the JSON string
        user_id = user_id_json['user_id']  # get the value of user_id
        print("user_id")
        print(user_id)
        print(type(user_id))
        

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
        try:
            audio_data, status_code, headers = generate_audio("output",selected_text)
            return audio_data, status_code, headers 
        except Exception as e:
            print(str(e))
            return jsonify(message='Error retrieving the audio from ElevenLabs'), 500

@app.route('/play-summary',methods=["POST"])
def play_summary():
    if request.method == "POST":
        headline = request.get_json()["headline"]
        print(headline)
        # with open(f'./audio/{headline}.mp3', "rb") as file:
        #     audio_data = file.read()
        #     return audio_data, 200, {'Content-Type': 'audio/mpeg'}
        try:
            audio_data, status_code, headers = generate_audio(headline,headline)
            return audio_data, status_code, headers 
        except Exception as e:
            print(str(e))
            return jsonify(message='Error retrieving the audio from ElevenLabs'), 500

@app.route('/')
def index():
     return render_template('index.html')

def generate_audio(headline, selected_text):
    # Voice using Eleven API 
    voice= "Bella"                                                                                                                                                                                                                             

    # Get current timestamp 
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S") 

    # File name with timestamp 
    #nombre_archivo = f"audio{timestamp}.mp3" 
    nombre_archivo = f'./audio/{headline}.mp3'
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



if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=8501)

