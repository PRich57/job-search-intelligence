import os
import unittest
from unittest.mock import MagicMock, patch

from app.models.job_listing import JobListing
from app.services.data_collection import JobDataCollector

class TestJobDataCollector(unittest.TestCase):
    def setUp(self):
        self.adzuna_client = MagicMock()
        self.usa_jobs_client = MagicMock()
        self.collector = JobDataCollector(self.adzuna_client, self.usa_jobs_client)

    def test_search_jobs(self):
        # Mock the fetch_jobs method of both clients
        self.adzuna_client.fetch_jobs.return_value = [
            JobListing("Software Developer", "Company A", "New York", "Description", 50000, 100000, "Adzuna", "http://apply.com")
        ]
        self.usa_jobs_client.fetch_jobs.return_value = [
            JobListing("Data Analyst", "Company B", "Washington", "Description", 60000, 120000, "USA Jobs", "http://apply.gov")
        ]

        jobs = self.collector.search_jobs()

        self.assertEqual(len(jobs), 12)  # 3 jobs * 4 job titles
        self.assertEqual(jobs[0].job_title, "Software Developer")
        self.assertEqual(jobs[1].job_title, "Data Analyst")

    @patch('app.services.data_collection.pd.DataFrame.to_csv')
    @patch('app.services.data_collection.os.makedirs')
    def test_save_to_csv(self, mock_makedirs, mock_to_csv):
        jobs = [
            JobListing("Software Developer", "Company A", "New York", "Description", 50000, 100000, "Adzuna", "http://apply.com"),
            JobListing("Data Analyst", "Company B", "Washington", "Description", 60000, 120000, "USA Jobs", "http://apply.gov")
        ]

        self.collector.save_to_csv(jobs, "test_output.csv")

        mock_makedirs.assert_called_once_with(os.path.dirname("test_output.csv"), exist_ok=True)
        mock_to_csv.assert_called_once_with("test_output.csv", index=False)

if __name__ == '__main__':
    unittest.main()