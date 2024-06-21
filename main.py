import logging
from datetime import datetime

from dotenv import load_dotenv

from analyze_data import analyze_data
from api_clients import AdzunaAPIClient, USAJobsAPIClient
from collect_data import JobDataCollector


# Set up logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Load environment variables
load_dotenv()


def main() -> None:
    adzuna_client = AdzunaAPIClient()
    usa_jobs_client = USAJobsAPIClient()

    collector = JobDataCollector(adzuna_client, usa_jobs_client)

    try:
        jobs = collector.collect_jobs(
            query="junior software developer",
            location="Denver, CO",
            distance=50,
            remote=True,
            max_experience=5,
            limit=50
        )

        if not jobs:
            logger.warning("No jobs were found. Check your search criteria and API keys.")
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            collector.save_to_csv(jobs, f"../../job-listings/job_listings_{timestamp}.csv")

            analysis = analyze_data(jobs)
            logger.info("Data Analysis Results:")
            for key, value in analysis.items():
                logger.info(f"{key}: {value}")
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()