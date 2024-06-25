import logging
from abc import ABC, abstractmethod
from typing import List

import requests
from ratelimit import limits, sleep_and_retry

from job_listing import JobListing
from config import (
    ADZUNA_APP_ID, ADZUNA_API_KEY, ADZUNA_BASE_URL,
    USA_JOBS_API_KEY, USA_JOBS_EMAIL, USA_JOBS_BASE_URL,
    DEFAULT_DISTANCE, DEFAULT_REMOTE, DEFAULT_MAX_EXPERIENCE, DEFAULT_LIMIT
)

logger = logging.getLogger(__name__)

class JobAPIClient(ABC):
    @abstractmethod
    def fetch_jobs(self, query: str, location: str, distance: int, remote: bool, max_experience: int, limit: int) -> List[JobListing]:
        pass

class AdzunaAPIClient(JobAPIClient):
    def __init__(self) -> None:
        self.app_id = ADZUNA_APP_ID
        self.api_key = ADZUNA_API_KEY
        self.base_url = ADZUNA_BASE_URL

    @sleep_and_retry
    @limits(calls=100, period=60)
    def fetch_jobs(self, query: str, location: str, distance: int = DEFAULT_DISTANCE, remote: bool = DEFAULT_REMOTE, max_experience: int = DEFAULT_MAX_EXPERIENCE, limit: int = DEFAULT_LIMIT) -> List[JobListing]:
        params = {
            "app_id": self.app_id,
            "app_key": self.api_key,
            "results_per_page": limit,
            "what": query,
            "where": location,
            "distance": distance,
            "max_days_old": 30,
            "content-type": "application/json"
        }
        if remote:
            params["where"] = f"{location} AND remote"

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            jobs_data = response.json()["results"]

            logger.info(f"Adzuna API returned {len(jobs_data)} jobs")
            logger.debug(f"First job location: {jobs_data[0]['location']['display_name'] if jobs_data else 'N/A'}")

            return [
                job_listing for job_listing in
                (self._create_job_listing(job) for job in jobs_data)
                if job_listing is not None and self._check_experience(job, max_experience)
            ]
        except requests.RequestException as e:
            logger.error(f"Error fetching jobs from Adzuna: {e}")
            logger.error(f"Response content: {response.text}")
            logger.error(f"Request URL: {response.url}")
            logger.error(f"Request parameters: {params}")
            return []
        
    def _create_job_listing(self, job: dict) -> JobListing | None:
        job_location = job.get("location", {}).get("display_name", "").lower()
        if "denver" not in job_location and "colorado" not in job_location:
            return None

        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")
        
        logger.debug(f"Raw salary data: min={salary_min}, max={salary_max}")

        if salary_min is None and salary_max is not None:
            salary_min = salary_max
        elif salary_max is None and salary_min is not None:
            salary_max = salary_min

        logger.debug(f"Processed salary data: min={salary_min}, max={salary_max}")

        return JobListing(
            job_title=job.get("title", "N/A"),
            company_name=job.get("company", {}).get("display_name", "N/A"),
            job_location=job_location,
            job_description=job.get("description", "N/A"),
            salary_low=salary_min,
            salary_high=salary_max,
            source="Adzuna"
        )
        
    def _check_experience(self, job: dict, max_experience: int) -> bool:
        return "experience" not in job["description"].lower() or f"{max_experience} years" in job["description"].lower()


class USAJobsAPIClient(JobAPIClient):
    def __init__(self) -> None:
        self.auth_key = USA_JOBS_API_KEY
        self.email = USA_JOBS_EMAIL
        self.base_url = USA_JOBS_BASE_URL

    @sleep_and_retry
    @limits(calls=50, period=60)
    def fetch_jobs(self, query: str, location: str, distance: int = DEFAULT_DISTANCE, remote: bool = DEFAULT_REMOTE, max_experience: int = DEFAULT_MAX_EXPERIENCE, limit: int = DEFAULT_LIMIT) -> List[JobListing]:
        headers = {
            "Authorization-Key": self.auth_key,
            "User-Agent": self.email,
            "Host": "data.usajobs.gov",
        }
        params = {
            "Keyword": query,
            "LocationName": location,
            "ResultsPerPage": limit,
        }
        # Removing potentially problematic parameters
        # if remote:
        #     params["RemoteIndicator"] = "Yes"

        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            jobs_data = response.json()["SearchResult"]["SearchResultItems"]

            logger.info(f"USA Jobs API returned {len(jobs_data)} jobs")
            return [
                self._create_job_listing(job)
                for job in jobs_data
                if self._check_experience(job, max_experience)
            ]
        except requests.RequestException as e:
            logger.error(f"Error fetching jobs from USA Jobs: {e}")
            logger.error(f"Response content: {response.text}")
            logger.error(f"Request URL: {response.url}")
            logger.error(f"Request headers: {headers}")
            logger.error(f"Request parameters: {params}")
            if response.status_code == 400:
                logger.error("400 Bad Request: This could be due to invalid parameters or authentication issues.")
                logger.error(f"Please check your USA_JOBS_API_KEY and USA_JOBS_EMAIL in the config file.")
            return []
        
    def _create_job_listing(self, job: dict) -> JobListing:
        job_data = job["MatchedObjectDescriptor"]
        return JobListing(
            job_title=job_data.get("PositionTitle", "N/A"),
            company_name=job_data.get("OrganizationName", "N/A"),
            job_location=job_data.get("PositionLocationDisplay", "N/A"),
            job_description=job_data.get("QualificationSummary", "N/A"),
            salary_low=float(job_data["PositionRemuneration"][0]["MinimumRange"]) if job_data.get("PositionRemuneration") else None,
            salary_high=float(job_data["PositionRemuneration"][0]["MaximumRange"]) if job_data.get("PositionRemuneration") else None,
            source="USA Jobs"
        )
        
    def _check_experience(self, job: dict, max_experience: int) -> bool:
        qualifications = job["MatchedObjectDescriptor"]["QualificationSummary"].lower()
        return "experience" not in qualifications or f"{max_experience} years" in qualifications
    
    # USA job codes: [(422, Data Analyst), (621, Software Developer)] - found on codelist/cyberworkroles - verify then add to filters