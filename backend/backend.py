from flask import Flask, request, jsonify
from flask_cors import CORS
from psycopg2 import pool, Error
import ai21
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import os
from flask import Flask, render_template
from elevenlabs import generate
import datetime

app = Flask(__name__)
CORS(app)
# Constants
AUDIO_FORMAT = "audio/mp3"
# Leer las variables de entorno
api_key = os.getenv('AI21_API_KEY')
db_password = os.getenv('DB_PASSWORD')
eleven_api_key = os.getenv('ELEVEN_API_KEY')

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=30,
    host='localhost',
    port=5432,
    user='postgres',
    password=db_password,
    dbname='postgres'
)

ai21.api_key = api_key


def valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


@app.route('/save-link', methods=["POST"])
def save_link():
    if request.method == "POST":
        body = request.get_json()
        url = body['url']
        user_id = body['user_id']
        
        if not valid_url(url):
            return jsonify(message="Invalid URL"), 400

        try:
            with connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 FROM user_links WHERE user_id = %s AND link = %s", (user_id, url))
                    if cur.fetchone() is None:
                        cur.execute("INSERT INTO user_links (user_id, link) VALUES (%s, %s)", (user_id, url))
                        conn.commit()
                        return jsonify(success=True)
                    else:
                        return jsonify(message="Link already exists"), 409
        except Error as e:
            return jsonify(message=str(e)), 500


@app.route('/get-links', methods=["POST"])
def get_links():
    if request.method == "POST":
        body = request.get_json()
        user_id = body['user_id']
        
        try:
            with connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT link FROM user_links WHERE user_id = %s", (user_id,))
                    links = [link for link, in cur.fetchall()]
            return jsonify(links=links)
        except Error as e:
            return jsonify(message=str(e)), 500


@app.route('/summarize-and-save', methods=["POST"])
def summarize_and_save():
    if request.method == "POST":
        body = request.get_json()
        url = body['url']
        user_id = body['user_id']
        
        if not valid_url(url):
            return jsonify(message="Invalid URL"), 400

        # Configurar opciones de Chrome
        chrome_options = Options()
        chrome_options.binary_location = os.getenv('CHROME_PATH')
        # Crear una instancia del controlador de Chrome
        driver = webdriver.Chrome(os.getenv('CHROMEDRIVER_PATH'), options=chrome_options)
        # Navegar a la URL utilizando Selenium
        driver.get(url)
        # Esperar 10 segundos
        time.sleep(10)
        # Obtener el contenido de la página
        content = driver.page_source
        # Cerrar el navegador
        driver.quit()
        # Continuar con el resto del código
        soup = BeautifulSoup(content, 'html.parser')
        transcript = ' '.join(soup.stripped_strings)
        # Imprimir el contenido de 'soup'
        print('Contenido de soup:')
        print(soup)

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
                    cur.execute(
                        "INSERT INTO summaries (user_id, link, summary) VALUES (%s, %s, %s)",
                        (user_id, url, summary["summary"])
                    )
                conn.commit()
            return jsonify(success=True)
        except Error as e:
            return jsonify(message=str(e)), 500

@app.route('/get-summaries', methods=["POST"])
def get_summaries():
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
        except Error as e:
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
        # Obtener la marca de tiempo actual
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # Nombre del archivo con la marca de tiempo
        nombre_archivo = f"audio{timestamp}.mp3"

        try:
            # Generate audio using Eleven API
            audio = generate(text=selected_text, voice=voice,api_key=eleven_api_key)

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
   app.run(debug=True, host='0.0.0.0', port=8501)

