import logging
from datetime import datetime

from config import LOG_LEVEL, LOG_FORMAT, OUTPUT_DIR, ADZUNA_APP_ID, ADZUNA_API_KEY, USA_JOBS_API_KEY, USA_JOBS_EMAIL
from analyze_data import analyze_data
from api_clients import AdzunaAPIClient, USAJobsAPIClient
from collect_data import JobDataCollector
from visualize_data import generate_visualizations

# Set up logging
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

def main() -> None:
    logger.info(f"Adzuna App ID: {'Set' if ADZUNA_APP_ID else 'Not set'}")
    logger.info(f"Adzuna API Key: {'Set' if ADZUNA_API_KEY else 'Not set'}")
    logger.info(f"USA Jobs API Key: {'Set' if USA_JOBS_API_KEY else 'Not set'}")
    logger.info(f"USA Jobs Email: {'Set' if USA_JOBS_EMAIL else 'Not set'}")

    adzuna_client = AdzunaAPIClient()
    usa_jobs_client = USAJobsAPIClient()

    collector = JobDataCollector(adzuna_client, usa_jobs_client)

    try:
        logger.info("Starting job collection...")
        jobs = collector.collect_jobs(
            query="software developer",
            location="Denver, CO",
            distance=50,
            # remote=True,
            max_experience=5,
            limit=100
        )

        logger.info(f"Collected {len(jobs)} jobs in total.")
        logger.info(f"Jobs from Adzuna: {len([job for job in jobs if job.source == 'Adzuna'])}")
        logger.info(f"Jobs from USA Jobs: {len([job for job in jobs if job.source == 'USA Jobs'])}")

        for job in jobs:
            logger.debug(f"Job: {job.job_title} at {job.company_name} in {job.job_location}")

        if not jobs:
            logger.warning("No jobs were found. Check your search criteria and API keys.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{OUTPUT_DIR}/job_listings_{timestamp}.csv"
        collector.save_to_csv(jobs, filename)

        analysis = analyze_data(jobs)
        logger.info("Data Analysis Results:")
        for key, value in analysis.items():
            logger.info(f"{key}: {value}")

        generate_visualizations(jobs)

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()