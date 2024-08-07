import os
from datetime import datetime

import pandas as pd
from quart import Quart, render_template, jsonify, request

from app.utils import format_salary_range
from app.services.data_collection import JobDataCollector
from app.services.api_clients import AdzunaAPIClient, USAJobsAPIClient
from config import active_config as Config

# Create the Quart application with the correct template folder
app = Quart(__name__, static_folder='app/static', template_folder='app/templates')

def load_latest_csv() -> pd.DataFrame | None:
    csv_files = [f for f in os.listdir(Config.OUTPUT_DIR) if f.endswith('.csv')]
    if not csv_files:
        print("No CSV files found in the directory.")
        return None
    latest_file = max(csv_files, key=lambda x: os.path.getctime(os.path.join(Config.OUTPUT_DIR, x)))
    file_path = os.path.join(Config.OUTPUT_DIR, latest_file)
    print(f"Loading file: {file_path}")
    return pd.read_csv(file_path)

@app.route('/')
async def index() -> str:
    return await render_template('index.html')

@app.route('/api/jobs')
async def get_jobs() -> dict:
    df = load_latest_csv()
    if df is None:
        print("No data loaded.")
        return jsonify({"data": []})
    
    # Get filters from request
    title_filters = request.args.getlist("titles[]")

    # Apply title filters if any
    if title_filters:
        df = df[df['job_title'].isin(title_filters)]
    
    # Limit the number of records
    df = df.head(1000)  # Limit to 1000 records
    
    # Convert DataFrame to list of dicts
    data = df.to_dict('records')
    
    # Ensure all values are JSON serializable and format salaries
    for record in data:
        # Format salaries and create salary range
        record['salary_range'] = format_salary_range(record['salary_low'], record['salary_high'])
        
        # Format other float values
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
            elif isinstance(value, float) and key not in ['salary_low', 'salary_high']:
                record[key] = round(value, 2)
    
    # Return in the format expected by DataTables
    return jsonify({"data": data})

@app.route('/api/job_titles')
async def get_job_titles() -> dict:
    df = load_latest_csv()
    if df is None:
        print("No data loaded.")
        return jsonify({"titles": []})
    
    titles = sorted(df['job_title'].unique().tolist())
    return jsonify({"titles": titles})

@app.route('/api/job_categories')
async def get_job_categories() -> dict:
    df = load_latest_csv()
    if df is None:
        print("No data loaded.")
        return jsonify({"categories": []})
    
    categories = sorted(df['job_category'].unique().tolist())
    return jsonify({"categories": categories})

@app.route('/api/category_stats')
async def get_category_stats() -> dict:
    df = load_latest_csv()
    if df is None:
        print("No data loaded.")
        return jsonify({"stats": []})
    
    stats = df['job_category'].value_counts().reset_index()
    stats.columns = ['category', 'count']
    return jsonify({"stats": stats.to_dict('records')})

@app.route('/api/fetch_all_jobs')
async def fetch_all_jobs() -> dict:
    Config.ADZUNA_CLIENT = AdzunaAPIClient()
    Config.USA_JOBS_CLIENT = USAJobsAPIClient()
    collector = JobDataCollector(Config.ADZUNA_CLIENT, Config.USA_JOBS_CLIENT)

    all_jobs = await collector.async_search_jobs(Config.DEFAULT_JOB_TITLES, Config.DEFAULT_LOCATIONS)

    adzuna_response = Config.ADZUNA_CLIENT.last_response if hasattr(Config.ADZUNA_CLIENT, 'last_response') else {}
    usa_jobs_response = Config.USA_JOBS_CLIENT.last_response if hasattr(Config.USA_JOBS_CLIENT, 'last_response') else {}

    return jsonify({
        "adzuna": adzuna_response,
        "usa_jobs": usa_jobs_response,
        "job_count": len(all_jobs)
    })

if __name__ == '__main__':
    app.run(debug=True)