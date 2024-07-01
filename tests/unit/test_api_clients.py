import unittest
from unittest.mock import patch, MagicMock
from app.services.api_clients import AdzunaAPIClient, USAJobsAPIClient, JobListing
from config import Config

class TestAdzunaAPIClient(unittest.TestCase):
    def setUp(self):
        self.client = AdzunaAPIClient()

    @patch('app.services.api_clients.requests.get')
    def test_fetch_jobs_success(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Software Developer",
                    "company": {"display_name": "Tech Corp"},
                    "location": {"display_name": "New York, NY"},
                    "description": "Great job opportunity",
                    "salary_min": 50000,
                    "salary_max": 100000,
                    "redirect_url": "https://example.com/apply"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        jobs = self.client.fetch_jobs("Software Developer", "New York", False, 10, 5, 1)

        self.assertEqual(len(jobs), 1)
        self.assertIsInstance(jobs[0], JobListing)
        self.assertEqual(jobs[0].job_title, "Software Developer")
        self.assertEqual(jobs[0].company_name, "Tech Corp")

    @patch('app.services.api_clients.requests.get')
    def test_fetch_jobs_api_error(self, mock_get):
        mock_get.side_effect = Exception("API Error")

        jobs = self.client.fetch_jobs("Software Developer", "New York", False, 10, 5, 1)

        self.assertEqual(len(jobs), 0)

class TestUSAJobsAPIClient(unittest.TestCase):
    def setUp(self):
        self.client = USAJobsAPIClient()

    @patch('app.services.api_clients.requests.get')
    def test_fetch_jobs_success(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "SearchResult": {
                "SearchResultItems": [
                    {
                        "MatchedObjectDescriptor": {
                            "PositionTitle": "Software Engineer",
                            "OrganizationName": "Department of Defense",
                            "PositionLocationDisplay": "Washington, DC",
                            "QualificationSummary": "Bachelor's degree required",
                            "PositionRemuneration": [{"MinimumRange": "60000", "MaximumRange": "120000"}],
                            "ApplyURI": ["https://example.com/apply"],
                            "JobCategory": [{"Name": "Information Technology", "Code": "2210"}]
                        }
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        jobs = self.client.fetch_jobs("Software Engineer", "Washington, DC", False, 10, 5, 1)

        self.assertEqual(len(jobs), 1)
        self.assertIsInstance(jobs[0], JobListing)
        self.assertEqual(jobs[0].job_title, "Software Engineer")
        self.assertEqual(jobs[0].company_name, "Department of Defense")

    @patch('app.services.api_clients.requests.get')
    def test_fetch_jobs_api_error(self, mock_get):
        mock_get.side_effect = Exception("API Error")

        jobs = self.client.fetch_jobs("Software Engineer", "Washington, DC", False, 10, 5, 1)

        self.assertEqual(len(jobs), 0)

if __name__ == '__main__':
    unittest.main()