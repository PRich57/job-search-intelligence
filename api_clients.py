import logging
import os
from abc import ABC, abstractmethod

import requests
from ratelimit import limits, sleep_and_retry

from job_listing import JobListing


logger = logging.getLogger(__name__)


class JobAPIClient(ABC):
    @abstractmethod
    def fetch_jobs(self, query: str, location: str, distance: int, remote: bool, max_experience: int, limit: int) -> list[JobListing]:
        pass


class AdzunaAPIClient(JobAPIClient):
    def __init__(self) -> None:
        self.app_id = os.getenv('ADZUNA_APP_ID')
        self.api_key = os.getenv('ADZUNA_API_KEY')
        self.base_url = "https://api.adzuna.com/v1/api/jobs/us/search/1"

    @sleep_and_retry
    @limits(calls=100, period=60)
    def fetch_jobs(self, query: str, location: str, distance: int = 50, remote: bool = True, max_experience: int = 5, limit: int = 50) -> list[JobListing]:
        params = {
            'app_id': self.app_id,
            'app_key': self.api_key,
            'results_per_page': limit,
            'what': query,
            'where': location,
            'distance': distance,
            'max_days_old': 30, # Ensure recent postings
            'content-type': 'application/json'
        }
        if remote: 
            params['where'] = 'remote'

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            jobs_data = response.json()['results']

            return [
                self._create_job_listing(job)
                for job in jobs_data
                if self._check_experience(job, max_experience)
            ]
        except requests.RequestException as e:
            logger.error(f"Error fetching jobs from Adzuna: {e}")
            return []
        
    def _create_job_listing(self, job: dict) -> JobListing:
        return JobListing(
            job_title=job.get('title', 'N/A'),
            company_name=job.get('company', {}).get('display_name', 'N/A'),
            job_location=job.get('location', {}).get('display_name', 'N/A'),
            job_description=job.get('description', 'N/A'),
            salary_low=job.get('salary_min'),
            salary_high=job.get('salary_max'),
            source='Adzuna'
        )
        
    def _check_experience(self, job: dict, max_experience: int) -> bool:
        # Simplistic check for now, return to implement more sophisticated parsing
        return 'experience' not in job['description'].lower() or f"{max_experience} years" in job['description'].lower()


class USAJobsAPIClient(JobAPIClient):
    def __init__(self) -> None:
        self.auth_key = os.getenv('USA_JOBS_API_KEY')
        self.email = os.getenv('USA_JOBS_EMAIL')
        self.base_url = "https://data.usajobs.gov/api/search"

    @sleep_and_retry
    @limits(calls=50, period=60)
    def fetch_jobs(self, query: str, location: str, distance: int = 50, remote: bool = True, max_experience: int = 5, limit: int = 50) -> list[JobListing]:
        headers = {
            'Authorization-Key': self.auth_key,
            'User-Agent': self.email,
            'Host': 'data.usajobs.gov',
        }
        params = {
            'Keyword': query,
            'LocationName': location,
            'ResultsPerPage': limit,
            'Radius': distance,
        }
        if remote:
            params['RemoteIndicator'] = 'Yes'

        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            jobs_data = response.json()['SearchResult']['SearchResultItems']

            return [
                self._create_job_listing(job)
                for job in jobs_data
                if self._check_experience(job, max_experience)
            ]
        except requests.RequestException as e:
            logger.error(f"Error fetching jobs from USA Jobs: {e}")
            logger.debug(f"USA Jobs API request details: URL: {response.url}, Headers: {headers}, Params: {params}")
            logger.debug(f"USA Jobs API response: {response.text}")
            return []
        
    def _create_job_listing(self, job: dict) -> JobListing:
        job_data = job['MatchedObjectDescriptor']
        return JobListing(
            job_title=job_data.get('PositionTitle', 'N/A'),
            company_name=job_data.get('OrganizationName', 'N/A'),
            job_location=job_data.get('PositionLocationDisplay', 'N/A'),
            job_description=job_data.get('QualificationSummary', 'N/A'),
            salary_low=float(job_data['PositionRemuneration'][0]['MinimumRange']) if job_data.get('PositionRemuneration') else None,
            salary_high=float(job_data['PositionRemuneration'][0]['MaximumRange']) if job_data.get('PositionRemuneration') else None,
            source='USA Jobs'
        )
        
    def _check_experience(self, job: dict, max_experience: int) -> bool:
        # Simplistic check for now, return to implement more sophisticated parsing
        qualifications = job['MatchObjectDescriptor']['QualificationSummary'].lower()
        return 'experience' not in qualifications or f"{max_experience} years" in qualifications
    

    # USA job codes: [(422, Data Analyst), (621, Software Developer)] - found on codelist/cyberworkroles - verify then add to filters