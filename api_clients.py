import logging
from abc import ABC, abstractmethod
from urllib.parse import quote, urlencode

import requests
from ratelimit import limits, sleep_and_retry

from job_listing import JobListing
import config

logger = logging.getLogger(__name__)

class JobAPIClient(ABC):
    @abstractmethod
    def fetch_jobs(self, query: str, location: str | None, remote: bool, distance: int | None, max_experience: int, limit: int) -> list[JobListing]:
        pass

    def _filter_senior_titles(self, job_listings: list[JobListing]) -> list[JobListing]:
        senior_title_indicators = ["senior", "sr", "lead", "2", "3", "4", "5", "ii", "iii", "iv", "manager", "expert", "director", "principal"]
        return [
            job for job in job_listings 
            if not any(word in job.job_title.lower() for word in senior_title_indicators)
        ]

class AdzunaAPIClient(JobAPIClient):
    def __init__(self) -> None:
        self.app_id = config.ADZUNA_APP_ID
        self.api_key = config.ADZUNA_API_KEY
        self.base_url = config.ADZUNA_BASE_URL

    @sleep_and_retry
    @limits(calls=100, period=60)
    def fetch_jobs(self, query: str, location: str | None, remote: bool, distance: int | None, max_experience: int, limit: int) -> list[JobListing]:
        params = {
            "app_id": self.app_id,
            "app_key": self.api_key,
            "results_per_page": limit,
            "what": query,
            "max_days_old": 30,
            "content-type": "application/json"
        }
        if remote:
            params["where"] = "remote"
        elif location:
            params["where"] = location
            if distance:
                params["distance"] = distance

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            jobs_data = response.json()["results"]

            job_listings = [
                self._create_job_listing(job)
                for job in jobs_data
                if self._check_experience(job, max_experience)
            ]
            
            filtered_listings = self._filter_senior_titles(job_listings)
            logger.info(f"Filtered out {len(job_listings) - len(filtered_listings)} senior job listings from Adzuna results")
            
            return filtered_listings
        except requests.RequestException as e:
            logger.error(f"Error fetching jobs from Adzuna: {e}")
            return []
        
    def _create_job_listing(self, job: dict[str, any]) -> JobListing:
        return JobListing(
            job_title=job.get("title", "N/A"),
            company_name=job.get("company", {}).get("display_name", "N/A"),
            job_location=job.get("location", {}).get("display_name", "N/A"),
            job_description=job.get("description", "N/A"),
            salary_low=job.get("salary_min"),
            salary_high=job.get("salary_max"),
            source="Adzuna",
            application_url=job.get("redirect_url", "N/A")
        )
        
    def _check_experience(self, job: dict[str, any], max_experience: int) -> bool:
        return "experience" not in job["description"].lower() or f"{max_experience} years" in job["description"].lower()

class USAJobsAPIClient(JobAPIClient):
    def __init__(self) -> None:
        self.auth_key = config.USA_JOBS_API_KEY
        self.email = config.USA_JOBS_EMAIL
        self.base_url = config.USA_JOBS_BASE_URL

    @sleep_and_retry
    @limits(calls=50, period=60)
    def fetch_jobs(self, query: str, location: str | None, remote: bool, distance: int | None, max_experience: int, limit: int) -> list[JobListing]:
        headers = {
            "Authorization-Key": self.auth_key,
            "User-Agent": self.email,
            "Host": "data.usajobs.gov",
        }
        params = {
            "PositionTitle": query,
            "ResultsPerPage": limit,
            "SecurityClearance": "Not Required",
        }

        if remote:
            params["RemoteIndicator"] = "True"
        elif location:
            params["LocationName"] = location
            if distance:
                params["Radius"] = distance

        encoded_params = urlencode(params, safe="", quote_via=quote)
        url = f"{self.base_url}?{encoded_params}"

        logger.debug(f"USAJobs API request URL: {url}")
        logger.debug(f"USAJobs API request headers: {headers}")

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response_json = response.json()
            
            logger.debug(f"USAJobs API response status: {response.status_code}")
            logger.debug(f"USAJobs API response headers: {response.headers}")
            logger.debug(f"USAJobs API response JSON keys: {response_json.keys()}")
            
            if "SearchResult" in response_json:
                search_result = response_json["SearchResult"]
                logger.debug(f"USAJobs SearchResult keys: {search_result.keys()}")
                
                if "SearchResultItems" in search_result:
                    jobs_data = search_result["SearchResultItems"]
                    logger.debug(f"Number of jobs found: {len(jobs_data)}")
                else:
                    logger.warning("No SearchResultItems found in the USAJobs API response")
                    return []
            else:
                logger.warning("No SearchResult found in the USAJobs API response")
                return []

            job_listings = [
                self._create_job_listing(job)
                for job in jobs_data
                if self._check_experience(job, max_experience)
            ]
            
            filtered_listings = self._filter_senior_titles(job_listings)
            logger.info(f"Filtered out {len(job_listings) - len(filtered_listings)} senior job listings from USAJobs results")
            
            return filtered_listings

        except requests.RequestException as e:
            logger.error(f"Error fetching jobs from USA Jobs: {e}")
            logger.debug(f"USA Jobs API response: {response.text}")
            return []
        
    def _create_job_listing(self, job: dict[str, any]) -> JobListing:
        job_data = job["MatchedObjectDescriptor"]
        return JobListing(
            job_title=job_data.get("PositionTitle", "N/A"),
            company_name=job_data.get("OrganizationName", "N/A"),
            job_location=job_data.get("PositionLocationDisplay", "N/A"),
            job_description=job_data.get("QualificationSummary", "N/A"),
            salary_low=float(job_data["PositionRemuneration"][0]["MinimumRange"]) if job_data.get("PositionRemuneration") else None,
            salary_high=float(job_data["PositionRemuneration"][0]["MaximumRange"]) if job_data.get("PositionRemuneration") else None,
            source="USA Jobs",
            application_url=job_data.get("ApplyURI", ["N/A"])[0]
        )
        
    def _check_experience(self, job: dict[str, any], max_experience: int) -> bool:
        qualifications = job["MatchedObjectDescriptor"].get("QualificationSummary", "").lower()
        logger.debug(f"Checking experience for job: {job['MatchedObjectDescriptor'].get('PositionTitle', 'N/A')}")
        logger.debug(f"Qualifications: {qualifications[:100]}...")  # Log first 100 characters of qualifications
        
        if "experience" not in qualifications:
            logger.debug("No experience mentioned, including job")
            return True
        
        for i in range(max_experience + 1):
            if f"{i} year" in qualifications:
                logger.debug(f"Found {i} year(s) experience requirement, including job")
                return True
        
        logger.debug("Experience requirement exceeds maximum, excluding job")
        return False