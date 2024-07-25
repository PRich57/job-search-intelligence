import asyncio
import logging
import os
from datetime import datetime

import pandas as pd
import aiohttp

from app.models.job_listing import JobListing
from config import active_config as Config

logger = logging.getLogger(__name__)

class JobDataCollector:
    def __init__(self, adzuna_client, usa_jobs_client):
        self.adzuna_client = adzuna_client
        self.usa_jobs_client = usa_jobs_client

    async def async_search_jobs(self, job_titles: list[str], locations: list[str]) -> list[JobListing]:
        queries = [
            {
                'query': job_title,
                'location': location,
                'remote': location.lower() == "remote",
                'distance': Config.DEFAULT_DISTANCE if location.lower() != "remote" else None,
                'max_experience': Config.DEFAULT_MAX_EXPERIENCE,
                'limit': Config.DEFAULT_LIMIT,
            }
            for job_title in job_titles
            for location in locations
        ]

        timeout = aiohttp.ClientTimeout(total=120)  # 2 minutes timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            adzuna_task = self.adzuna_client.async_fetch_jobs_batch(session, queries)
            usajobs_task = self.usa_jobs_client.async_fetch_jobs_batch(session, queries)
            
            adzuna_jobs, usajobs_jobs = await asyncio.gather(adzuna_task, usajobs_task)
            
            logger.info(f"Adzuna jobs: {len(adzuna_jobs)}")
            logger.info(f"USA Jobs: {len(usajobs_jobs)}")
            
            all_jobs = adzuna_jobs + usajobs_jobs

        unique_jobs = self._deduplicate_jobs(all_jobs)
        
        logger.info(f"Total unique jobs found: {len(unique_jobs)}")
        return unique_jobs

    def _deduplicate_jobs(self, jobs: list[JobListing]) -> list[JobListing]:
        job_dict = {}
        for job in jobs:
            key = (job.job_title, job.company_name, job.job_location, job.source)
            if key not in job_dict:
                job_dict[key] = job
            elif job.source == "USA Jobs":  # Prioritize USA Jobs listings
                job_dict[key] = job
        return list(job_dict.values())

    def save_to_csv(self, jobs, filename):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            df = pd.DataFrame([job.__dict__ for job in jobs])
            df["timestamp"] = datetime.now()
            df.to_csv(filename, index=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving data to CSV: {str(e)}")