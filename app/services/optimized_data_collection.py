import asyncio
from functools import lru_cache

import aiohttp

from app.models.job_listing import JobListing
from app.services.api_clients import AdzunaAPIClient, USAJobsAPIClient

class OptimizedJobDataCollector:
    def __init__(self, adzuna_client: AdzunaAPIClient, usa_jobs_client: USAJobsAPIClient):
        self.adzuna_client = adzuna_client
        self.usa_jobs_client = usa_jobs_client

    async def fetch_jobs_concurrently(self, job_titles: list[str], locations: list[str]) -> list[JobListing]:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for job_title in job_titles:
                for location in locations:
                    tasks.append(self.fetch_job(session, job_title, location, "adzuna"))
                    tasks.append(self.fetch_job(session, job_title, location, "usajobs"))
                
            results = await asyncio.gather(*tasks)
            return [job for sublist in results for job in sublist]

    async def fetch_job(self, session: aiohttp.ClientSession, job_title: str, location: str, source: str) -> list[JobListing]:
        if source == "adzuna":
            return await self.adzuna_client.async_fetch_jobs(session, job_title, location)
        elif source == "usajobs":
            return await self.usa_jobs_client.async_fetch_jobs(session, job_title, location)

    @lru_cache(maxsize=128)
    def get_cached_jobs(self, job_title: str, location: str) -> list[JobListing]:
        return asyncio.run(self.fetch_jobs_concurrently([job_title], [location]))
        
    def search_jobs(self, job_titles: list[str], locations: list[str]) -> list[JobListing]:
        return asyncio.run(self.fetch_jobs_concurrently(job_titles, locations))