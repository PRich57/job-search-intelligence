from flask import Blueprint, jsonify, request

from app.services.data_collection import JobDataCollector
from config import Config

api = Blueprint("api", __name__)

@api.route("/jobs")
def get_jobs():
    collector = JobDataCollector(Config.ADZUNA_CLIENT, Config.USA_JOBS_CLIENT)
    jobs = collector.search_jobs(Config.DEFAULT_JOB_TITLES)
    
    # Get title filters from the request
    title_filters = request.args.getlist("titles[]")
    
    # Apply title filters if any
    if title_filters:
        jobs = [job for job in jobs if job.job_title in title_filters]
    
    # Limit the number of records
    jobs = jobs[:1000]  # Limit to 1000 records
    
    # Convert jobs to dictionaries
    job_dicts = [job.__dict__ for job in jobs]
    
    # Format salaries
    for job in job_dicts:
        job["salary_range"] = format_salary_range(job["salary_low"], job["salary_high"])
    
    return jsonify({"data": job_dicts})

@api.route("/job_titles")
def get_job_titles():
    collector = JobDataCollector(Config.ADZUNA_CLIENT, Config.USA_JOBS_CLIENT)
    jobs = collector.search_jobs(Config.DEFAULT_JOB_TITLES)
    titles = sorted(set(job.job_title for job in jobs))
    return jsonify({"titles": titles})

@api.route("/job_categories")
def get_job_categories():
    collector = JobDataCollector(Config.ADZUNA_CLIENT, Config.USA_JOBS_CLIENT)
    jobs = collector.search_jobs(Config.DEFAULT_JOB_TITLES)
    categories = sorted(set(job.job_category for job in jobs))
    return jsonify({"categories": categories})

@api.route("/category_stats")
def get_category_stats():
    collector = JobDataCollector(Config.ADZUNA_CLIENT, Config.USA_JOBS_CLIENT)
    jobs = collector.search_jobs(Config.DEFAULT_JOB_TITLES)
    category_counts = {}
    for job in jobs:
        category_counts[job.job_category] = category_counts.get(job.job_category, 0) + 1
    stats = [{"category": cat, "count": count} for cat, count in category_counts.items()]
    return jsonify({"stats": stats})

@api.route("/fetch_all_jobs")
async def fetch_all_jobs():
    collector = JobDataCollector(Config.ADZUNA_CLIENT, Config.USA_JOBS_CLIENT)
    jobs = await collector.async_search_jobs(Config.DEFAULT_JOB_TITLES, Config.DEFAULT_LOCATIONS)
    return jsonify({"adzuna": [job.__dict__ for job in jobs if job.source == "Adzuna"],
                    "usa_jobs": [job.__dict__ for job in jobs if job.source == "USA Jobs"],
                    "job_count": len(jobs)})

def format_salary_range(low: float | None, high: float | None) -> str:
    if low is None and high is None:
        return "N/A"
    elif low is None:
        return f"Up to ${high:,.2f}"
    elif high is None:
        return f"${low:,.2f}+"
    elif low == high:
        return f"${low:,.2f}"
    else:
        return f"${low:,.2f} - ${high:,.2f}"

def create_api_routes(app):
    app.register_blueprint(api, url_prefix="/api")