import logging
from datetime import datetime

import pandas as pd

from api_clients import AdzunaAPIClient, USAJobsAPIClient
from job_listing import JobListing
import config

logger = logging.getLogger(__name__)

class JobDataCollector:
    def __init__(self, adzuna_client: AdzunaAPIClient, usa_jobs_client: USAJobsAPIClient) -> None:
        self.adzuna_client = adzuna_client
        self.usa_jobs_client = usa_jobs_client

    def collect_jobs(self, query: str, location: str | None, remote: bool = config.DEFAULT_REMOTE, 
                     distance: int = config.DEFAULT_DISTANCE, max_experience: int = config.DEFAULT_MAX_EXPERIENCE, 
                     limit: int = config.DEFAULT_LIMIT, source: str = "all") -> list[JobListing]:
        if source == "adzuna":
            return self.adzuna_client.fetch_jobs(query, location, remote, distance, max_experience, limit)
        elif source == "usajobs":
            return self.usa_jobs_client.fetch_jobs(query, location, remote, distance, max_experience, limit)
        else:
            adzuna_jobs = self.adzuna_client.fetch_jobs(query, location, remote, distance, max_experience, limit)
            usa_jobs = self.usa_jobs_client.fetch_jobs(query, location, remote, distance, max_experience, limit)
            return adzuna_jobs + usa_jobs
    
    def save_to_csv(self, jobs: list[JobListing], filename: str) -> None:
        df = pd.DataFrame([
            {
                "job_title": job.job_title,
                "company_name": job.company_name,
                "job_location": job.job_location,
                "job_description": job.job_description,
                "salary_low": job.salary_low,
                "salary_high": job.salary_high,
                "source": job.source,
                "application_url": job.application_url,
                "timestamp": datetime.now()
            }
            for job in jobs
        ])
        df.to_csv(filename, index=False)
        logger.info(f"Data saved to {filename}")