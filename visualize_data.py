import matplotlib.pyplot as plt
from typing import List
from job_listing import JobListing

def plot_top_companies(jobs: List[JobListing], top_n: int = 10):
    company_counts = {}
    for job in jobs:
        company_counts[job.company_name] = company_counts.get(job.company_name, 0) + 1
    
    sorted_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    companies, counts = zip(*sorted_companies)

    plt.figure(figsize=(12, 6))
    plt.bar(companies, counts)
    plt.title(f"Top {top_n} Companies by Job Listings")
    plt.xlabel("Company")
    plt.ylabel("Number of Job Listings")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("top_companies.png")
    plt.close()

def plot_salary_distribution(jobs: List[JobListing]):
    salaries = [(job.salary_low + job.salary_high) / 2 for job in jobs if job.salary_low and job.salary_high]
    
    plt.figure(figsize=(10, 6))
    plt.hist(salaries, bins=20, edgecolor="black")
    plt.title("Salary Distribution")
    plt.xlabel("Salary")
    plt.ylabel("Frequency")
    plt.savefig("salary_distribution.png")
    plt.close()

def generate_visualizations(jobs: List[JobListing]):
    plot_top_companies(jobs)
    plot_salary_distribution(jobs)
    print("Visualizations have been saved as 'top_companies.png' and 'salary_distribution.png'.")