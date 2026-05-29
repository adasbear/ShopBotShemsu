import sys
import os

PROJECT_PATH = "/home/adilararsa/ShopBotShemsu"

if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

# Load .env so environment variables are available
from dotenv import load_dotenv
dotenv_path = os.path.join(PROJECT_PATH, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from main import app as application
