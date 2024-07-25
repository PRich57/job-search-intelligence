import asyncio
import logging
import json
import random
from abc import ABC, abstractmethod
from functools import lru_cache

import aiohttp

from app.models.job_listing import JobListing
from config import active_config as Config

logger = logging.getLogger(__name__)

class JobAPIClient(ABC):
    @abstractmethod
    async def async_fetch_jobs_batch(self, session, queries: list[dict]) -> list[JobListing]:
        pass

    @abstractmethod
    def _create_job_listing(self, job: dict) -> JobListing:
        pass

    @abstractmethod
    def _check_experience(self, job: dict, max_experience: int) -> bool:
        pass

    def filter_jobs(self, job_listings: list[JobListing]) -> list[JobListing]:
        senior_title_indicators = [
            "senior", "sr", "lead", "2", "3", "4", "5",
            "ii", "iii", "iv", "manager", "expert", "director", "principal"
        ]
        relevant_categories = {"2210", "0854", "1530", "1550", "N/A"}

        filtered_jobs = [
            job for job in job_listings
            if job.job_category_code in relevant_categories
            and not any(word in job.job_title.lower() for word in senior_title_indicators)
        ]
        
        logger.info(f"Filtered {len(job_listings) - len(filtered_jobs)} jobs")
        logger.info(f"Remaining jobs: {len(filtered_jobs)}")
        
        return filtered_jobs

class AdzunaAPIClient(JobAPIClient):
    def __init__(self):
        self.app_id = Config.ADZUNA_APP_ID
        self.api_key = Config.ADZUNA_API_KEY
        self.base_url = Config.ADZUNA_BASE_URL
        self.semaphore = asyncio.Semaphore(2)  # Reduced to 2 concurrent requests

    async def async_fetch_jobs_batch(self, session, queries: list[dict]) -> list[JobListing]:
        all_jobs = []
        tasks = []

        for query in queries:
            task = asyncio.create_task(self._fetch_single_query_with_retry(session, json.dumps(query)))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        for job_listings in results:
            all_jobs.extend(job_listings)

        logger.info(f"Total Adzuna jobs before filtering: {len(all_jobs)}")
        filtered_jobs = self.filter_jobs(all_jobs)
        logger.info(f"Total Adzuna jobs after filtering: {len(filtered_jobs)}")
        return filtered_jobs

    @lru_cache(maxsize=32)
    async def _fetch_single_query_with_retry(self, session, query_json, max_retries=3):
        query = json.loads(query_json)
        for attempt in range(max_retries):
            try:
                async with self.semaphore:
                    return await self._fetch_single_query(session, query)
            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    logger.warning(f"Rate limit exceeded. Retrying in {wait_time:.2f} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Error fetching jobs from Adzuna: {e}")
                    return []
            except Exception as e:
                logger.error(f"Unexpected error when fetching jobs from Adzuna: {e}")
                return []
        logger.error(f"Max retries reached for query: {query}")
        return []

    async def _fetch_single_query(self, session, query):
        params = {
            "app_id": self.app_id,
            "app_key": self.api_key,
            "results_per_page": query.get('limit', 100),
            "what": query['query'],
            "where": query['location'] if not query.get('remote') else "remote",
            "content-type": "application/json"
        }
        if query.get('distance'):
            params["distance"] = query['distance']

        async with session.get(self.base_url, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            jobs_data = data.get("results", [])
            logger.info(f"Adzuna query for {params['what']} in {params['where']} returned {len(jobs_data)} jobs")
            job_listings = [
                self._create_job_listing(job)
                for job in jobs_data
                if self._check_experience(job, query.get('max_experience', 5))
            ]
            logger.info(f"After experience check: {len(job_listings)} jobs")
            return job_listings

    def _create_job_listing(self, job: dict) -> JobListing:
        return JobListing(
            job_title=job.get("title", "N/A"),
            company_name=job.get("company", {}).get("display_name", "N/A"),
            job_location=job.get("location", {}).get("display_name", "N/A"),
            job_description=job.get("description", "N/A"),
            salary_low=job.get("salary_min"),
            salary_high=job.get("salary_max"),
            source="Adzuna",
            application_url=job.get("redirect_url", "N/A"),
            job_category="N/A",
            job_category_code="N/A"
        )
        
    def _check_experience(self, job: dict, max_experience: int) -> bool:
        return "experience" not in job["description"].lower() or f"{max_experience} years" in job["description"].lower()

class USAJobsAPIClient(JobAPIClient):
    def __init__(self):
        self.auth_key = Config.USA_JOBS_API_KEY
        self.email = Config.USA_JOBS_EMAIL
        self.base_url = Config.USA_JOBS_BASE_URL

    async def async_fetch_jobs_batch(self, session, queries: list[dict]) -> list[JobListing]:
        all_jobs = []
        tasks = []

        for query in queries:
            headers = {
                "Authorization-Key": self.auth_key,
                "User-Agent": self.email,
                "Host": "data.usajobs.gov"
            }
            params = {
                "PositionTitle": query['query'],
                "ResultsPerPage": query.get('limit', 100),
                "SecurityClearance": "Not Required",
            }

            if query.get('remote'):
                params["RemoteIndicator"] = "True"
            elif query['location']:
                params["LocationName"] = query['location']
                if query.get('distance'):
                    params["Radius"] = query['distance']

            tasks.append(self._fetch_single_query(session, headers, params, query.get('max_experience', 5)))

        results = await asyncio.gather(*tasks)
        for job_listings in results:
            all_jobs.extend(job_listings)

        return self.filter_jobs(all_jobs)

    async def _fetch_single_query(self, session, headers, params, max_experience):
        try:
            async with session.get(self.base_url, headers=headers, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                jobs_data = data.get("SearchResult", {}).get("SearchResultItems", [])
                return [
                    self._create_job_listing(job)
                    for job in jobs_data
                    if self._check_experience(job, max_experience)
                ]
        except aiohttp.ClientResponseError as e:
            logger.error(f"Error fetching jobs from USA Jobs: {e}")
        except Exception as e:
            logger.error(f"Unexpected error when fetching jobs from USA Jobs: {e}")
        return []

    def _create_job_listing(self, job: dict) -> JobListing:
        job_data = job["MatchedObjectDescriptor"]
        job_categories = job_data.get("JobCategory", [])
        job_category = job_categories[0]["Name"] if job_categories else "N/A"
        job_category_code = job_categories[0]["Code"] if job_categories else "N/A"
        
        return JobListing(
            job_title=job_data.get("PositionTitle", "N/A"),
            company_name=job_data.get("OrganizationName", "N/A"),
            job_location=job_data.get("PositionLocationDisplay", "N/A"),
            job_description=job_data.get("QualificationSummary", "N/A"),
            salary_low=float(job_data["PositionRemuneration"][0]["MinimumRange"]) if job_data.get("PositionRemuneration") else None,
            salary_high=float(job_data["PositionRemuneration"][0]["MaximumRange"]) if job_data.get("PositionRemuneration") else None,
            source="USA Jobs",
            application_url=job_data.get("ApplyURI", ["N/A"])[0],
            job_category=job_category,
            job_category_code=job_category_code
        )
        
    def _check_experience(self, job: dict, max_experience: int) -> bool:
        qualifications = job["MatchedObjectDescriptor"].get("QualificationSummary", "").lower()
        if "experience" not in qualifications:
            return True
        for i in range(max_experience + 1):
            if f"{i} year" in qualifications:
                return True
        return False