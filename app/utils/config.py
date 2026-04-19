from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()  # load your environment codes for .env

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = (
    BASE_DIR / "data"
)  ## Base dir is a path object so just add "/" to combine pathes [don't need for os.path.join()]
PDF_DIR = DATA_DIR / "pdfs"
WEB_DIR = DATA_DIR / "web"
CHROMA_DIR = BASE_DIR / "chroma_db"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
