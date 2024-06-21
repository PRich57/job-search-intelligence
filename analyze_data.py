import pandas as pd

from job_listing import JobListing


def analyze_data(jobs: list[JobListing]) -> dict[str, object]:
    df = pd.DataFrame([job.__dict__ for job in jobs])

    analysis = {
        'total_jobs': len(df),
        'jobs_by_source': df['source'].value_counts().to_dict(),
        'top_companies': df['company_name'].value_counts().head(5).to_dict(),
        'top_locations': df['job_location'].value_counts().head(5).to_dict(),
    }

    # Calculate average salary where available
    salary_data = df[df['salary_low'].notna() & df['salary_high'].notna()]
    if not salary_data.empty:
        analysis['avg_salary_low'] = salary_data['salary_low'].mean()
        analysis['avg_salary_high'] = salary_data['salary_high'].mean()

    return analysis