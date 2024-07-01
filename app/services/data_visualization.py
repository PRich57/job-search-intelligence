import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from app.models.job_listing import JobListing
from config import active_config as Config

def generate_visualizations(jobs: list[JobListing]) -> None:
    df = pd.DataFrame([job.__dict__ for job in jobs])

    # Ensure output directory exists
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

    # Job count by source
    plt.figure(figsize=(10, 6))
    sns.countplot(x="source", data=df)
    plt.title("Job Count by Source")
    plt.savefig(os.path.join(Config.OUTPUT_DIR, "job_count_by_source.png"))
    plt.close()

    # Top companies
    plt.figure(figsize=(12, 6))
    top_companies = df["company_name"].value_counts().head(10)
    sns.barplot(x=top_companies.index, y=top_companies.values)
    plt.title("Top 10 Companies by Job Listings")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(Config.OUTPUT_DIR, "top_companies.png"))
    plt.close()

    # Salary distribution
    plt.figure(figsize=(10, 6))
    salary_data = df[df["salary_low"].notna() & df["salary_high"].notna()]
    sns.histplot(data=salary_data, x="salary_low", kde=True)
    plt.title("Distribution of Minimum Salaries")
    plt.savefig(os.path.join(Config.OUTPUT_DIR, "salary_distribution.png"))
    plt.close()

    # Job categories
    plt.figure(figsize=(12, 6))
    top_categories = df["job_category"].value_counts().head(10)
    sns.barplot(x=top_categories.index, y=top_categories.values)
    plt.title("Top 10 Job Categories")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(Config.OUTPUT_DIR, "top_job_categories.png"))
    plt.close()