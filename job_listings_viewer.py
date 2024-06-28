from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
from config import active_config as Config
from app.utils import format_salary_range

# Create the Flask application with the correct template folder
app = Flask(__name__, template_folder='app/templates')

def load_latest_csv():
    csv_files = [f for f in os.listdir(Config.OUTPUT_DIR) if f.endswith('.csv')]
    if not csv_files:
        print("No CSV files found in the directory.")
        return None
    latest_file = max(csv_files, key=lambda x: os.path.getctime(os.path.join(Config.OUTPUT_DIR, x)))
    file_path = os.path.join(Config.OUTPUT_DIR, latest_file)
    print(f"Loading file: {file_path}")
    return pd.read_csv(file_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/jobs')
def get_jobs():
    df = load_latest_csv()
    if df is None:
        print("No data loaded.")
        return jsonify({"data": []})
    
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
def get_job_titles():
    df = load_latest_csv()
    if df is None:
        print("No data loaded.")
        return jsonify({"titles": []})
    
    titles = sorted(df['job_title'].unique().tolist())
    return jsonify({"titles": titles})

@app.route('/api/job_categories')
def get_job_categories():
    df = load_latest_csv()
    if df is None:
        print("No data loaded.")
        return jsonify({"categories": []})
    
    categories = sorted(df['job_category'].unique().tolist())
    return jsonify({"categories": categories})

@app.route('/api/category_stats')
def get_category_stats():
    df = load_latest_csv()
    if df is None:
        print("No data loaded.")
        return jsonify({"stats": []})
    
    stats = df['job_category'].value_counts().reset_index()
    stats.columns = ['category', 'count']
    return jsonify({"stats": stats.to_dict('records')})

if __name__ == '__main__':
    app.run(debug=True)