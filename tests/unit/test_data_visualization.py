import os
import unittest
from unittest.mock import MagicMock, patch

from app.models.job_listing import JobListing
from app.services.data_visualization import generate_visualizations

class TestDataVisualization(unittest.TestCase):
    def setUp(self):
        self.jobs = [
            JobListing("Software Developer", "Company A", "New York", "Description", 50000, 100000, "Adzuna", "http://apply.com"),
            JobListing("Data Analyst", "Company B", "Washington", "Description", 60000, 120000, "USA Jobs", "http://apply.gov"),
            JobListing("Software Engineer", "Company A", "San Francisco", "Description", 80000, 160000, "Adzuna", "http://apply.com"),
            JobListing("Web Developer", "Company C", "Chicago", "Description", 55000, 110000, "USA Jobs", "http://apply.gov")
        ]

    @patch('app.services.data_visualization.plt')
    @patch('app.services.data_visualization.sns')
    @patch('app.services.data_visualization.os.makedirs')
    def test_generate_visualizations(self, mock_makedirs, mock_sns, mock_plt):
        mock_figure = MagicMock()
        mock_plt.figure.return_value = mock_figure

        generate_visualizations(self.jobs)

        # Check if the output directory was created
        mock_makedirs.assert_called_once_with("job-listings", exist_ok=True)

        # Check if the required plots were created
        self.assertEqual(mock_plt.figure.call_count, 4)
        self.assertEqual(mock_plt.close.call_count, 4)
        self.assertEqual(mock_sns.countplot.call_count, 1)
        self.assertEqual(mock_sns.barplot.call_count, 2)
        self.assertEqual(mock_sns.histplot.call_count, 1)

        # Check if the plots were saved
        expected_calls = [
            unittest.mock.call(os.path.join("job-listings", "job_count_by_source.png")),
            unittest.mock.call(os.path.join("job-listings", "top_companies.png")),
            unittest.mock.call(os.path.join("job-listings", "salary_distribution.png")),
            unittest.mock.call(os.path.join("job-listings", "top_job_categories.png"))
        ]
        mock_plt.savefig.assert_has_calls(expected_calls, any_order=True)

if __name__ == '__main__':
    unittest.main()