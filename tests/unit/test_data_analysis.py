import unittest
from app.services.data_analysis import analyze_data
from app.models.job_listing import JobListing

class TestDataAnalysis(unittest.TestCase):
    def setUp(self):
        self.jobs = [
            JobListing("Software Developer", "Company A", "New York", "Description", 50000, 100000, "Adzuna", "http://apply.com"),
            JobListing("Data Analyst", "Company B", "Washington", "Description", 60000, 120000, "USA Jobs", "http://apply.gov"),
            JobListing("Software Engineer", "Company A", "San Francisco", "Description", 80000, 160000, "Adzuna", "http://apply.com"),
            JobListing("Web Developer", "Company C", "Chicago", "Description", 55000, 110000, "USA Jobs", "http://apply.gov")
        ]

    def test_analyze_data(self):
        analysis = analyze_data(self.jobs)

        self.assertEqual(analysis["total_jobs"], 4)
        self.assertEqual(analysis["jobs_by_source"], {"Adzuna": 2, "USA Jobs": 2})
        self.assertEqual(analysis["top_companies"], {"Company A": 2, "Company B": 1, "Company C": 1})
        self.assertEqual(analysis["top_locations"], {"New York": 1, "Washington": 1, "San Francisco": 1, "Chicago": 1})
        self.assertAlmostEqual(analysis["avg_salary_low"], 61250, delta=0.01)
        self.assertAlmostEqual(analysis["avg_salary_high"], 122500, delta=0.01)

if __name__ == '__main__':
    unittest.main()