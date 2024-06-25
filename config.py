import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY")
USA_JOBS_API_KEY = os.getenv("USA_JOBS_API_KEY")
USA_JOBS_EMAIL = os.getenv("USA_JOBS_EMAIL")

# API Endpoints
ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs/us/search/1"
USA_JOBS_BASE_URL = "https://data.usajobs.gov/api/search"

# Default search parameters
DEFAULT_DISTANCE = 50
DEFAULT_REMOTE = True
DEFAULT_MAX_EXPERIENCE = 5
DEFAULT_LIMIT = 50

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Output directory for CSV files
OUTPUT_DIR = "job_listings"