import logging
from datetime import datetime

from dotenv import load_dotenv

from analyze_data import analyze_data
from api_clients import AdzunaAPIClient, USAJobsAPIClient
from collect_data import JobDataCollector


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Load environment variables
load_dotenv()


def main() -> None:
    adzuna_client = AdzunaAPIClient()
    usa_jobs_client = USAJobsAPIClient()

    collector = JobDataCollector(adzuna_client, usa_jobs_client)

    jobs = collector.collect_jobs("data analyst", "Denver", limit=50)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    collector.save_to_csv(jobs, f"job_listings_{timestamp}.csv")

    analysis = analyze_data(jobs)
    logger.info("Data Analysis Results:")
    for key, value in analysis.items():
        logger.info(f"{key}: {value}")


if __name__ == "__main__":
    main()