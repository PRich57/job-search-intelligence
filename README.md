# Job Search Intelligence

## Overview
Job Search Intelligence is a Python-based tool designed to collect, analyze, and visualize job listing data from multiple sources. It aims to provide insights into the job market, helping job seekers make informed decisions about their career paths. The project includes a web interface for easy exploration of job data.

## Motivation
I created this project to assist me in my job search on multiple levels. It pulls job postings from a multitude of sources, allowing me to set my own filters and search preferences. I can extract exactly what I need from each posting and create data that helps me see trends for the specific titles I'm interested in. Not only is it excellent practice for my coding skills, but it will also look great on my resume and portfolio. This project showcases my ability to work with APIs, handle data processing, and create useful visualizations, all while solving a real-world problem that's personally relevant to me.

## Features
- Multi-source job data collection (Adzuna, USA Jobs)
- Advanced data analysis and visualization
- Customizable job search parameters
- Interactive web interface for exploring job listings
- CSV export of collected data
- RESTful API for accessing job data

## Requirements
- Python 3.9 or later

The project is compatible with a range of library versions. Below are the minimum supported versions along with the versions currently used in development (in parentheses):

- Flask 2.1.0 or later (3.0.3)
- Werkzeug 2.0.0 or later (3.0.3)
- numpy 1.20.0 or later (2.0.0)
- pandas 1.3.5 or later (2.2.2)
- matplotlib 3.5.1 or later (3.9.0)
- seaborn 0.11.2 or later (0.13.2)
- requests 2.27.1 or later (2.32.3)
- python-dotenv 0.19.2 or later (1.0.1)
- pytest 6.2.5 or later (8.2.2)
- ratelimit 2.2.1 or later (2.2.1)

Users can install either the minimum supported versions or the latest compatible versions. My goal is to maintain compatibility across a range of versions to provide flexibility for different development environments.

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/PRich57/job-search-intelligence.git
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
   FLASK_ENV=development  # Change to 'production' for production environment
   ```

## Usage
1. Run the main script to collect and analyze job data:
   ```
   python run.py
   ```

2. Start the web server to explore job listings:
   ```
   python job_listings_viewer.py
   ```

3. Open a web browser and navigate to `http://localhost:5000` to access the job listings viewer.

## Project Structure
```
job-search-intelligence/
├── app/
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── static/
│   ├── templates/
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
├── tests/
├── .github/
├── config.py
├── run.py
├── job_listings_viewer.py
├── requirements.txt
├── .gitignore
├── .env
├── .env.example
└── README.md
```

## API Endpoints
- `/api/jobs`: Get all job listings
- `/api/job_titles`: Get all unique job titles
- `/api/job_categories`: Get all unique job categories
- `/api/category_stats`: Get job count statistics by category

## Future Improvements
I have several ideas for enhancing this project in the future:

* Additional API integrations to expand job source diversity
* Enhanced data visualizations for specific search criteria
* Improved UI/UX for a more intuitive user experience
* User preferences to replace hardcoded filters and job titles
* User profiles for saving and managing personalized search criteria (job titles, location, salary range, etc.)
* Interactive visualization dashboard for deeper insights
* Updated analyses (trend reports for open positions, salary ranges, remote v in-office, etc.)
* Transition to purely front-end usage for improved performance
* Integration of an LLM to clean up job descriptions and extract mentions of experience level/years
* Addition of a security clearance requirement filter
* Bug Fixes: 
   * Include remote status in the location field for remote positions
   * UI detail tweaks for grammatical correctness and readability 
   * Replace "N/A" in visualizations with accurate results from Adzuna

I'm continuously working on improving this project, so expect more features and bug fixes in the future!

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Testing
Run the test suite using:
```
python -m pytest tests
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Adzuna API for providing job listing data
- USA Jobs API for providing government job listings