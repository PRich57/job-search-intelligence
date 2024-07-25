import logging
import os
from datetime import datetime

import pandas as pd
import asyncio
import aiohttp

from app.models.job_listing import JobListing
from config import active_config as Config

logger = logging.getLogger(__name__)

class JobDataCollector:
    def __init__(self, adzuna_client, usa_jobs_client):
        self.adzuna_client = adzuna_client
        self.usa_jobs_client = usa_jobs_client

    def search_jobs(self, job_titles=None, locations=None):
        if job_titles is None:
            job_titles = Config.DEFAULT_JOB_TITLES
        if locations is None:
            locations = Config.DEFAULT_LOCATIONS

        return asyncio.run(self.async_search_jobs(job_titles, locations))

    async def async_search_jobs(self, job_titles, locations):
        all_jobs = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for job_title in job_titles:
                for location in locations:
                    remote = location.lower() == "remote"
                    for source in ["adzuna", "usajobs"]:
                        logger.info(f"Fetching {'remote' if remote else 'local'} {job_title} jobs in {location} from {source.capitalize()}...")
                        task = self.async_collect_jobs(
                            session=session,
                            query=job_title,
                            location=None if remote else location,
                            remote=remote,
                            distance=Config.DEFAULT_DISTANCE if not remote else None,
                            max_experience=Config.DEFAULT_MAX_EXPERIENCE,
                            limit=Config.DEFAULT_LIMIT,
                            source=source
                        )
                        tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            for source_jobs in results:
                all_jobs.extend(source_jobs)
                logger.info(f"Found {len(source_jobs)} jobs")
        
        return all_jobs

    def collect_jobs(self, query, location, remote=Config.DEFAULT_REMOTE, 
                     distance=Config.DEFAULT_DISTANCE, max_experience=Config.DEFAULT_MAX_EXPERIENCE, 
                     limit=Config.DEFAULT_LIMIT, source="all"):
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

    async def async_collect_jobs(self, session, query, location, remote=Config.DEFAULT_REMOTE, 
                                 distance=Config.DEFAULT_DISTANCE, max_experience=Config.DEFAULT_MAX_EXPERIENCE, 
                                 limit=Config.DEFAULT_LIMIT, source="all"):
        try:
            if source == "adzuna":
                return await self.adzuna_client.async_fetch_jobs(session, query, location)
            elif source == "usajobs":
                return await self.usa_jobs_client.async_fetch_jobs(session, query, location)
            else:
                adzuna_jobs = await self.adzuna_client.async_fetch_jobs(session, query, location)
                usa_jobs = await self.usa_jobs_client.async_fetch_jobs(session, query, location)
                return adzuna_jobs + usa_jobs
        except Exception as e:
            logger.error(f"Error collecting jobs from {source}: {str(e)}")
            return []
    
    def save_to_csv(self, jobs, filename):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            df = pd.DataFrame([job.__dict__ for job in jobs])
            df["timestamp"] = datetime.now()
            df.to_csv(filename, index=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving data to CSV: {str(e)}")