import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env
load_dotenv()

def connect_to_mongodb(db_name, collection_name):
        uri = client = MongoClient(uri, server_api=ServerApi('1'))
        db = client[db_name]
        collection = db[collection_name]
        return collection

    except Exception as e:
        # Manejo de excepciones para errores de conexión
        print(f"Error al conectar con MongoDB: {e}")
        return None
