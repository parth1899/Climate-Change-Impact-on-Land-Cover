import os
from dotenv import load_dotenv
import ee

load_dotenv()

class Settings:
    EE_ACCOUNT = os.getenv("EE_ACCOUNT")
    EE_PRIVATE_KEY_FILE = os.getenv("EE_PRIVATE_KEY_FILE")

def initialize_earth_engine():
    try:
        credentials = ee.ServiceAccountCredentials(
            Settings.EE_ACCOUNT, 
            Settings.EE_PRIVATE_KEY_FILE
        )
        ee.Authenticate()
        ee.Initialize(credentials)
    except Exception as e:
        print(f"Earth Engine initialization failed: {str(e)}")
        raise
