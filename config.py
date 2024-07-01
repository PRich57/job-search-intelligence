import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # API Clients
    ADZUNA_CLIENT = None
    USA_JOBS_CLIENT = None

    # API Keys and credentials
    ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
    ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY")
    USA_JOBS_API_KEY = os.getenv("USA_JOBS_API_KEY")
    USA_JOBS_EMAIL = os.getenv("USA_JOBS_EMAIL")

    # API Base URLs
    ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs/us/search/1"
    USA_JOBS_BASE_URL = "https://data.usajobs.gov/api/search"

    # Default search settings
    DEFAULT_REMOTE = True
    DEFAULT_DISTANCE = 25  # in miles
    DEFAULT_MAX_EXPERIENCE = 5  # in years
    DEFAULT_LIMIT = 100  # number of job listings to fetch per request
    JOB_TITLES = [
        "Software Developer",
        "Data Analyst",
        "Software Engineer",
        "Web Developer"
    ]

    # Output directory for data and visualizations
    OUTPUT_DIR = "job-listings"

    # Logging configuration
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Flask configuration
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")  # Change this in production

    # Visualization settings
    CHART_STYLE = "darkgrid"
    COLOR_PALETTE = "deep"

    # Data analysis settings
    TOP_N_RESULTS = 10  # For top companies, locations, etc.

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

# Dictionary to easily switch between configurations
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}

# Set the active configuration
active_config = config[os.getenv("FLASK_ENV", "default")]