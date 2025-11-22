import os
from dotenv import load_dotenv

# Load variables from .env.local
load_dotenv(".env.local")

DATABASE_URL = os.getenv("DATABASE_URL")