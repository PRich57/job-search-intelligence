import logging
from datetime import datetime

from config import LOG_LEVEL, LOG_FORMAT, OUTPUT_DIR
from analyze_data import analyze_data
from api_clients import AdzunaAPIClient, USAJobsAPIClient
from collect_data import JobDataCollector
from visualize_data import generate_visualizations

# Set up logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

def main() -> None:
    adzuna_client = AdzunaAPIClient()
    usa_jobs_client = USAJobsAPIClient()

    collector = JobDataCollector(adzuna_client, usa_jobs_client)

    try:
        logger.info("Starting job collection...")
        jobs = collector.collect_jobs(
            query="junior software developer",
            location="Denver, CO"
        )

        logger.info(f"Collected {len(jobs)} jobs in total.")
        logger.info(f"Jobs from Adzuna: {len([job for job in jobs if job.source == 'Adzuna'])}")
        logger.info(f"Jobs from USA Jobs: {len([job for job in jobs if job.source == 'USA Jobs'])}")

        if not jobs:
            logger.warning("No jobs were found. Check your search criteria and API keys.")
        else:
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