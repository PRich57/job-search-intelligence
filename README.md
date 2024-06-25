# Job Search Intelligence

## Overview
Job Search Intelligence is a Python-based tool designed to collect, analyze, and visualize job listing data from multiple sources. It aims to provide insights into the job market, helping job seekers make informed decisions about their career paths.

## Features
- Multi-source job data collection (Adzuna, USA Jobs)
- Data analysis and visualization
- Customizable job search parameters
- CSV export of collected data

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/job-search-intelligence.git
   cd job-search-intelligence
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root and add your API keys:
   ```
   ADZUNA_APP_ID=your_adzuna_app_id
   ADZUNA_API_KEY=your_adzuna_api_key
   USA_JOBS_API_KEY=your_usa_jobs_api_key
   USA_JOBS_EMAIL=your_email@example.com
   ```

## Usage
Run the main script to collect and analyze job data:
```
python main.py
```

## Project Structure
- `analyze_data.py`: Functions for analyzing collected job data
- `api_clients.py`: API client classes for different job listing sources
- `collect_data.py`: Job data collection logic
- `job_listing.py`: JobListing data model
- `main.py`: Main application entry point

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.