import logging
from datetime import datetime

from app.services.data_collection import JobDataCollector
from app.services.data_analysis import analyze_data
from app.services.data_visualization import generate_visualizations
from app.api.routes import create_api_routes
from config import Config
from app.services.api_clients import AdzunaAPIClient, USAJobsAPIClient

logging.basicConfig(level=Config.LOG_LEVEL, format=Config.LOG_FORMAT)
logger = logging.getLogger(__name__)

def main() -> None:
    Config.ADZUNA_CLIENT = AdzunaAPIClient()
    Config.USA_JOBS_CLIENT = USAJobsAPIClient()

    collector = JobDataCollector(Config.ADZUNA_CLIENT, Config.USA_JOBS_CLIENT)

    try:
        # Search for remote jobs
        remote_jobs = collector.search_jobs(remote=True)

        # Search for local jobs in Denver, CO
        denver_jobs = collector.search_jobs(location="Denver, CO", remote=False)

        all_jobs = remote_jobs + denver_jobs

        if not all_jobs:
            logger.warning("No jobs were found. Check your search criteria and API keys.")
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{Config.OUTPUT_DIR}/job_listings_{timestamp}.csv"
            collector.save_to_csv(all_jobs, filename)
            logger.info(f"Saved {len(all_jobs)} jobs to {filename}")

            analysis = analyze_data(all_jobs)
            logger.info("Data Analysis Results:")
            for key, value in analysis.items():
                logger.info(f"{key}: {value}")

            generate_visualizations(all_jobs)

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()