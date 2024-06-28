import logging
import os
from datetime import datetime

import pandas as pd

from app.models.job_listing import JobListing
from config import active_config as Config

logger = logging.getLogger(__name__)

class JobDataCollector:
    def __init__(self, adzuna_client, usa_jobs_client):
        self.adzuna_client = adzuna_client
        self.usa_jobs_client = usa_jobs_client

    def search_jobs(self, location: str | None = None, remote: bool = Config.DEFAULT_REMOTE) -> list[JobListing]:
        all_jobs = []
        for job_title in Config.JOB_TITLES:
            for source in ["adzuna", "usajobs"]:
                logger.info(f"Fetching {'remote' if remote else 'local'} {job_title} jobs from {source.capitalize()}...")
                source_jobs = self.collect_jobs(
                    query=job_title,
                    location=location,
                    remote=remote,
                    distance=Config.DEFAULT_DISTANCE if location else None,
                    max_experience=Config.DEFAULT_MAX_EXPERIENCE,
                    limit=Config.DEFAULT_LIMIT,
                    source=source
                )
                logger.info(f"Found {len(source_jobs)} {job_title} jobs from {source.capitalize()}")
                all_jobs.extend(source_jobs)
        return all_jobs

    def collect_jobs(self, query: str, location: str | None, remote: bool = Config.DEFAULT_REMOTE, 
                     distance: int | None = Config.DEFAULT_DISTANCE, max_experience: int = Config.DEFAULT_MAX_EXPERIENCE, 
                     limit: int = Config.DEFAULT_LIMIT, source: str = "all") -> list[JobListing]:
        try:
            if source == "adzuna":
                return self.adzuna_client.fetch_jobs(query, location, remote, distance, max_experience, limit)
            elif source == "usajobs":
                return self.usa_jobs_client.fetch_jobs(query, location, remote, distance, max_experience, limit)
            else:
                adzuna_jobs = self.adzuna_client.fetch_jobs(query, location, remote, distance, max_experience, limit)
                usa_jobs = self.usa_jobs_client.fetch_jobs(query, location, remote, distance, max_experience, limit)
                return adzuna_jobs + usa_jobs
        except Exception as e:
            logger.error(f"Error collecting jobs from {source}: {str(e)}")
            return []
    
    def save_to_csv(self, jobs: list[JobListing], filename: str) -> None:
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            df = pd.DataFrame([job.__dict__ for job in jobs])
            df["timestamp"] = datetime.now()
            df.to_csv(filename, index=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving data to CSV: {str(e)}")