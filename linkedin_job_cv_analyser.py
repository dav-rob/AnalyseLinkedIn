import argparse

from llm_analyser import analyse_role_desc
from selenium_scraper import get_job_description_array
from sqlite_load import add_to_sqlite
from util.log_utils import print_array


def analyse_job_posts(url):
    scraped_jobs_array = get_job_description_array(url)
    analyse_role_desc(scraped_jobs_array)
    add_to_sqlite(scraped_jobs_array)


if __name__ == "__main__":
    # Set up the argument parser
    parser = argparse.ArgumentParser(description='Extract job description from a LinkedIn job page using Selenium.')
    parser.add_argument('url', type=str, help='The URL of the LinkedIn job page.')
    # Parse command-line arguments
    args = parser.parse_args()
    # Get the job description from the provided URL
    if '&' not in args.url:
        print("[WARNING] URL appears to be truncated. Please wrap the URL in quotes when running the script:")
        print('python linkedin_job_cv_analyser.py "YOUR_FULL_URL_HERE"')
        print("\nFor example:")
        print('python linkedin_job_cv_analyser.py "https://www.linkedin.com/jobs/search/?distance=25&geoId=101165590&keywords=engineering%20manager"')
        exit(1)
        
    print(f"[MAIN] Raw URL from args: {args.url}")
    analyse_job_posts(args.url)
