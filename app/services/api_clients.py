import logging
import json
from abc import ABC, abstractmethod
from urllib.parse import quote, urlencode

import requests
from ratelimit import limits, sleep_and_retry

from app.models.job_listing import JobListing
from config import active_config as config

logger = logging.getLogger(__name__)

class JobAPIClient(ABC):
    @abstractmethod
    def fetch_jobs(self, query: str, location: str | None, remote: bool, distance: int | None, max_experience: int, limit: int) -> list[JobListing]:
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

    def analyze_category_codes(self, job_listings: list[JobListing]) -> None:
        category_codes = {}
        for job in job_listings:
            category_codes[job.job_category_code] = category_codes.get(job.job_category_code, 0) + 1
        
        logger.info("Category code distribution:")
        for code, count in sorted(category_codes.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"{code}: {count}")

class AdzunaAPIClient(JobAPIClient):
    def __init__(self) -> None:
        self.app_id = config.ADZUNA_APP_ID
        self.api_key = config.ADZUNA_API_KEY
        self.base_url = config.ADZUNA_BASE_URL
        self.last_response = {}

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

            self.last_response = jobs_data

            job_listings = [
                self._create_job_listing(job)
                for job in jobs_data
                if self._check_experience(job, max_experience)
            ]
            
            self.analyze_category_codes(job_listings)
            filtered_listings = self.filter_jobs(job_listings)
            
            return filtered_listings
        except requests.RequestException as e:
            logger.error(f"Error fetching jobs from Adzuna: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error when fetching jobs from Adzuna: {e}")
            return []
        
    def _create_job_listing(self, job: dict) -> JobListing:
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
        
    def _check_experience(self, job: dict, max_experience: int) -> bool:
        return "experience" not in job["description"].lower() or f"{max_experience} years" in job["description"].lower()

class USAJobsAPIClient(JobAPIClient):
    def __init__(self) -> None:
        self.auth_key = config.USA_JOBS_API_KEY
        self.email = config.USA_JOBS_EMAIL
        self.base_url = config.USA_JOBS_BASE_URL
        self.last_response = {}

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
            jobs_data = response.json()["SearchResult"]["SearchResultItems"]

            self.last_response = jobs_data

            job_listings = [
                self._create_job_listing(job)
                for job in jobs_data
                if self._check_experience(job, max_experience)
            ]

            self.analyze_category_codes(job_listings)
            filtered_listings = self.filter_jobs(job_listings)
            
            return filtered_listings
        except requests.RequestException as e:
            logger.error(f"Error fetching jobs from USA Jobs: {e}")
            logger.debug(f"USA Jobs API response: {response.text if 'response' in locals() else 'No response'}")
            return []
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
        logger.debug(f"Checking experience for job: {job['MatchedObjectDescriptor'].get('PositionTitle', 'N/A')}")
        logger.debug(f"Qualifications: {qualifications[:100]}...")
        
        if "experience" not in qualifications:
            logger.debug("No experience mentioned, including job")
            return True
        
        for i in range(max_experience + 1):
            if f"{i} year" in qualifications:
                logger.debug(f"Found {i} year(s) experience requirement, including job")
                return True
        
        logger.debug("Experience requirement exceeds maximum, excluding job")
        return False