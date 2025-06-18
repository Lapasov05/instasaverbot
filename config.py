from dotenv import load_dotenv
import os
load_dotenv()

DB_NAME = os.getenv('POSTGRES_NAME')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_HOST = os.getenv('POSTGRES_HOST')
DB_USER = os.getenv('POSTGRES_USER')
x_rapidapi_key = os.getenv('x-rapidapi-key')
x_rapidapi_host = os.getenv('x-rapidapi-host')
x_rapidapi_key_youtube = os.getenv('x-rapidapi-key_youtube')
x_rapidapi_host_youtube = os.getenv('x-rapidapi-host_youtube')
API_TOKEN = "7388594042:AAESKhyq9nOt-zcH1m0W4bh_ivwfIe2r0wY"
CHANNEL_ID = '@english_movies_by_code'  # Replace with your channel ID


