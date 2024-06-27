from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
import json

app = Flask(__name__)

def load_latest_csv():
    directory = '../../job-listings'
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    if not csv_files:
        print("No CSV files found in the directory.")
        return None
    latest_file = max(csv_files, key=lambda x: os.path.getctime(os.path.join(directory, x)))
    file_path = os.path.join(directory, latest_file)
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
    
    # Limit the number of records and the length of text fields
    df = df.head(1000)  # Limit to 1000 records
    text_columns = ['job_title', 'company_name', 'job_location', 'job_description', 'application_url']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str[:500]  # Limit text fields to 500 characters
    
    # Convert DataFrame to list of dicts
    data = df.to_dict('records')
    
    # Ensure all values are JSON serializable
    for record in data:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
    
    # Return in the format expected by DataTables
    return jsonify({"data": data})

if __name__ == '__main__':
    app.run(debug=True)