# LinkedIn Analyzer Documentation

## Running The Analyzer

To run the analyzer, login to LinkedIn and go here https://www.linkedin.com/jobs/, put in the role and location you're interested in. Then paste the url of the search page into the command line below:

```bash
$ python linkedin_job_cv_analyser.py "<url>"
```

For example

```bash
$ python linkedin_job_cv_analyser.py "https://www.linkedin.com/jobs/search/?distance=25&geoId=101165590&keywords=engineering%20manager&origin=JOB_SEARCH_PAGE_KEYWORD_HISTORY&refresh=true"
```

The quotes around the url is important because some shells will interpret the & character as a special character to run in background. Better to remove any "currentJobId" in the parameters list for a time-independent search.
