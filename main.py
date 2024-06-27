import logging
from datetime import datetime

from api_clients import AdzunaAPIClient, USAJobsAPIClient
from collect_data import JobDataCollector
from analyze_data import analyze_data
from visualize_data import generate_visualizations
import config

# Set up logging
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

def search_jobs(collector: JobDataCollector, job_titles: list[str], location: str = None, remote: bool = config.DEFAULT_REMOTE) -> list:
    all_jobs = []
    for job_title in job_titles:
        for source in ["adzuna", "usajobs"]:
            logger.info(f"Fetching {'remote' if remote else 'local'} {job_title} jobs from {source.capitalize()}...")
            source_jobs = collector.collect_jobs(
                query=job_title,
                location=location,
                remote=remote,
                distance=config.DEFAULT_DISTANCE if location else None,
                max_experience=config.DEFAULT_MAX_EXPERIENCE,
                limit=config.DEFAULT_LIMIT,
                source=source
            )
            logger.info(f"Found {len(source_jobs)} {job_title} jobs from {source.capitalize()}")
            all_jobs.extend(source_jobs)
    return all_jobs

def main() -> None:
    adzuna_client = AdzunaAPIClient()
    usa_jobs_client = USAJobsAPIClient()

    collector = JobDataCollector(adzuna_client, usa_jobs_client)

    job_titles = ["Software Developer", "Data Analyst", "Software Engineer", "Web Developer"]

    try:
        # Search for remote jobs
        remote_jobs = search_jobs(collector, job_titles=job_titles, remote=True)

        # Search for local jobs in Denver, CO
        denver_jobs = search_jobs(collector, job_titles=job_titles, location="Denver, CO", remote=False)

        all_jobs = remote_jobs + denver_jobs

        if not all_jobs:
            logger.warning("No jobs were found. Check your search criteria and API keys.")
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{config.OUTPUT_DIR}/job_listings_{timestamp}.csv"
            collector.save_to_csv(all_jobs, filename)
            logger.info(f"Saved {len(all_jobs)} jobs to {filename}")

            analysis = analyze_data(all_jobs)
            logger.info("Data Analysis Results:")
            for key, value in analysis.items():
                logger.info(f"{key}: {value}")

            # Generate visualizations
            generate_visualizations(all_jobs)

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()