from dataclasses import dataclass


@dataclass
class JobListing:
    job_title: str
    company_name: str
    job_location: str
    job_description: str
    salary_low: float | None
    salary_high: float | None
    source: str