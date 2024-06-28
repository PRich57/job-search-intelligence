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
    application_url: str
    job_category: str = "N/A"
    job_category_code: str = "N/A"

    def __post_init__(self):
        if self.salary_low is not None and self.salary_high is not None:
            if self.salary_low > self.salary_high:
                self.salary_low, self.salary_high = self.salary_high, self.salary_low
        elif self.salary_low is not None and self.salary_high is None:
            self.salary_high = self.salary_low
        elif self.salary_high is not None and self.salary_low is None:
            self.salary_low = self.salary_high