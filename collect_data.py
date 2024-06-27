import logging
from datetime import datetime
from typing import List

import pandas as pd

from api_clients import AdzunaAPIClient, USAJobsAPIClient
from job_listing import JobListing
from config import DEFAULT_DISTANCE, DEFAULT_MAX_EXPERIENCE, DEFAULT_LIMIT

logger = logging.getLogger(__name__)

class JobDataCollector:
    def __init__(self, adzuna_client: AdzunaAPIClient, usa_jobs_client: USAJobsAPIClient) -> None:
        self.adzuna_client = adzuna_client
        self.usa_jobs_client = usa_jobs_client

    def collect_jobs(self, query: str, location: str, distance: int = DEFAULT_DISTANCE, max_experience: int = DEFAULT_MAX_EXPERIENCE, limit: int = DEFAULT_LIMIT) -> List[JobListing]:
        adzuna_jobs = self.adzuna_client.fetch_jobs(query, location, distance, max_experience, limit)
        usa_jobs = self.usa_jobs_client.fetch_jobs(query, location, distance, max_experience, limit)
        return adzuna_jobs + usa_jobs
    
    def save_to_csv(self, jobs: List[JobListing], filename: str) -> None:
        df = pd.DataFrame([job.__dict__ for job in jobs])
        df["timestamp"] = datetime.now()
        df.to_csv(filename, index=False)
        logger.info(f"Data saved to {filename}")