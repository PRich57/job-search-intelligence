import logging
from datetime import datetime
import asyncio

from app.services.data_collection import JobDataCollector
from app.services.data_analysis import analyze_data
from app.services.data_visualization import generate_visualizations
from config import Config
from app.services.api_clients import AdzunaAPIClient, USAJobsAPIClient

logging.basicConfig(level=Config.LOG_LEVEL, format=Config.LOG_FORMAT)
logger = logging.getLogger(__name__)

def get_user_input(prompt, default_values):
    user_input = input(f"{prompt} (default: {', '.join(default_values)}): ").strip()
    if user_input:
        return [item.strip() for item in user_input.split(',')]
    return default_values

async def async_main():
    Config.ADZUNA_CLIENT = AdzunaAPIClient()
    Config.USA_JOBS_CLIENT = USAJobsAPIClient()

    collector = JobDataCollector(Config.ADZUNA_CLIENT, Config.USA_JOBS_CLIENT)

    job_titles = get_user_input("Enter job titles (comma-separated)", Config.DEFAULT_JOB_TITLES)
    locations = get_user_input("Enter locations (comma-separated)", Config.DEFAULT_LOCATIONS)

    try:
        all_jobs = await collector.async_search_jobs(job_titles, locations)

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

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()