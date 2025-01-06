import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from sqlite_load import job_id_in_database

# from env_loader import get_env_key #use for loading username/password which is deprecated

def get_job_description_array(url):
    """
    Takes a url from the linkedIn Jobs Search page, finds the jobs list top level element,
    then scrolls that element to fill out the full list of jobs on that page, then selects
    each job link and scrapes the job description that is loaded and puts all the descriptions
    in an array.

    :param url: the linkedIn Jobs Search page particular to each person searching
    :return: an array of job descriptions from the LinkedIn Jobs Search page.
    """
    driver = configure_driver()
    login(driver)
    # Open the LinkedIn URL passed in by command line parameters
    driver.get(url)
    print("Page loaded, waiting for elements...")
    # Wait for any job-related content to load
    time.sleep(1)
    jobs_before_scrolling = get_job_cards(driver)
    print(f"Found {len(jobs_before_scrolling)} job items before scrolling")
    # Scroll down so all of the page is dynamically loaded before we scrape it
    if jobs_before_scrolling:
        scroll_jobs_list(driver)
        jobs_after_scrolling = get_job_cards(driver)
        if len(jobs_after_scrolling) > len(jobs_before_scrolling):
            jobs_before_scrolling = jobs_after_scrolling
            print(f"After scrolling, found {len(jobs_before_scrolling)} job items")
        else:
            # NB if there are only a couple of results then this isn't a problem
            print("PROBLEM: SCROLLING APPEARS NOT TO HAVE WORKED")
    else:
        raise Exception("No Job Cards Found")
    
    # Click on each element and extract the job description
    jobs_desc_array = click_job_card_get_info(driver, jobs_before_scrolling)
    # end program.
    driver.quit()
    return jobs_desc_array


def get_job_cards(driver):
    try:
        job_cards = driver.find_elements(By.CSS_SELECTOR,
                             ".job-card-container, .jobs-search-results__list-item, .jobs-search-two-pane__job-card-container")
        print(f"Found {len(job_cards)} job items")
        if not job_cards:
            raise Exception("No jobs found")
    except Exception as e:
        print(f"Error finding job items: {str(e)}")
    return job_cards



def configure_driver():
    """
    Configure Selenium driver with its options.

    :return: a configured Selenium driver
    """
    # Set up Chrome options for headless browsing
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_options.add_argument("--disable-gpu")  # Disable GPU usage for headless
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model (if necessary)
    # Set up the web driver with the appropriate options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver


def click_job_card_get_info(driver, jobs_list_el_array):
    """
    Loop through each element, check if the job_id is in the database
     then extract and add the database fields.

    :param driver: selenium driver
    :param jobs_list_el_array: the list of links to jobs
    :return: array of job descriptions
    """
    jobs_json = {"jobs_array": []}
    print(f"Found {len(jobs_list_el_array)} job elements")
    
    #for job_link_el in jobs_list_el_array:
    for i in range(4):
        job_link_el = jobs_list_el_array[i]
        try:
            print("Processing job listing...")
            # Try multiple selectors for job ID
            try:
                job_id = job_link_el.get_attribute("data-job-id")
                if not job_id:
                    job_id = job_link_el.find_element(By.CSS_SELECTOR, "[data-job-id]").get_attribute("data-job-id")
            except:
                print("Could not find job ID, skipping...")
                continue

            click_job(driver, job_id, job_link_el, jobs_json)
        except Exception as e:
            print(f"Error processing job: {str(e)}")
            continue
    # Count the number of items in the array
    jobs_list = jobs_json["jobs_array"]
    item_count = len(jobs_list)
    print(f"The jobs_json contains {item_count} items.")
    return jobs_list


def click_job(driver, job_id, job_link_el, jobs_json):
    job_link_el.click()
    time.sleep(0.5)
    single_job_json = {}
    if not job_id_in_database(job_id):
        # Try multiple selectors for job title using various strategies
        try:
            job_title_selectors = [
                "h1[class*='job-title']",
                "h1[class*='title']",
                ".t-24.t-bold",
                "[data-test-job-title]",
                "//*[contains(@class, 'job-title') or contains(@class, 'title')]//h1",  # XPath fallback
            ]
            job_title = None
            for selector in job_title_selectors:
                try:
                    if selector.startswith("//"):
                        job_title = driver.find_element(By.XPATH, selector).text.strip()
                    else:
                        job_title = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                    if job_title:
                        break
                except:
                    continue
            if not job_title:
                job_title = "Title not found"
        except:
            job_title = "Title not found"

        # Try multiple selectors for company name
        try:
            company_selectors = [
                "[data-test-employer-name]",
                "[class*='company-name']",
                "[class*='employer-name']",
                "//div[contains(@class, 'company') or contains(@class, 'employer')]//a",  # XPath fallback
            ]
            company = None
            for selector in company_selectors:
                try:
                    if selector.startswith("//"):
                        company = driver.find_element(By.XPATH, selector).text.strip()
                    else:
                        company = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                    if company:
                        break
                except:
                    continue
            if not company:
                company = "Company not found"
        except:
            company = "Company not found"

        # Try to get job details with enhanced selectors
        try:
            details_selectors = [
                "[class*='metadata-wrapper'], [class*='job-insight']",
                "[data-test-job-details]",
                "//*[contains(@class, 'metadata') or contains(@class, 'job-insight')]",
            ]
            job_details = []
            for selector in details_selectors:
                try:
                    if selector.startswith("//"):
                        elements = job_link_el.find_elements(By.XPATH, selector)
                    else:
                        elements = job_link_el.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        job_details = text_for_array_of_el(elements)
                        break
                except:
                    continue
        except:
            job_details = []

        # Try to get footer info with enhanced selectors
        try:
            footer_selectors = [
                "[class*='footer-item'], [class*='workplace-type']",
                "[data-test-workplace-type]",
                "//*[contains(@class, 'footer') or contains(@class, 'workplace')]",
            ]
            footer_info = []
            for selector in footer_selectors:
                try:
                    if selector.startswith("//"):
                        elements = job_link_el.find_elements(By.XPATH, selector)
                    else:
                        elements = job_link_el.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        footer_info = text_for_array_of_el(elements)
                        break
                except:
                    continue
        except:
            footer_info = []

        # Try multiple selectors for job description
        try:
            description_selectors = [
                "[class*='jobs-description']",
                "[data-test-job-description]",
                "//div[contains(@class, 'description')]",  # XPath fallback
            ]
            job_desc_txt = None
            for selector in description_selectors:
                try:
                    if selector.startswith("//"):
                        job_description_el = driver.find_element(By.XPATH, selector)
                    else:
                        job_description_el = driver.find_element(By.CSS_SELECTOR, selector)
                    job_desc_txt = job_description_el.text
                    if job_desc_txt:
                        break
                except:
                    continue
            if not job_desc_txt:
                job_desc_txt = "Description not found"
        except:
            print("Could not find job description")
            job_desc_txt = "Description not found"

        single_job_json["job_id"] = job_id
        single_job_json["job_title"] = job_title
        single_job_json["company"] = company
        single_job_json["job_details"] = job_details
        single_job_json["footer_info"] = footer_info
        single_job_json["job_desc_txt"] = job_desc_txt
        single_job_json["isNotInteresting"] = 0
        jobs_json["jobs_array"].append(single_job_json)
        print(f"Successfully processed job: {job_title} at company: {company}")
        print("---------------------------------------------------")


def text_for_array_of_el(elements):
    # List to store all the inner text
    all_inner_text = []
    # Iterate through each sub-element and get its text
    for element in elements:
        inner_text = element.text
        all_inner_text.append(inner_text)
    return all_inner_text


def login(driver):
    """
    Logs in by reading the cookies file loaded from a previous search session for a session id.
    The cookies method can produce more predictable search results and layout than username and
    password.

    :param driver: selenium driver
    """
    # Navigate to LinkedIn to set the domain
    driver.get("https://linkedin.com/uas/login")
    # waiting for the page to load
    time.sleep(1)
    print("*** Using cookies")
    load_cookie_session(driver)
    time.sleep(1)


def load_cookie_session(driver):
    """
    Load cookies from the file that has been preloaded with a cookie session-id after logging in manually.


    :param driver: selenium web driver
    :return: None
    """
    with open('cookies/linkedin_cookies.json', 'r') as f:
        cookies = json.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)


def get_scrollable_div_by_footer(driver):
    """
    Find the scrollable container by locating the footer and getting its parent.
    
    :param driver: selenium webdriver
    :return: scrollable element or None if not found
    """
    try:
        footer = driver.find_element(By.CSS_SELECTOR, "footer.global-footer-compact")
        scrollable_div = footer.find_element(By.XPATH, "./..")
        
        # Verify if it's actually scrollable
        overflow_y = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).getPropertyValue('overflow-y')", 
            scrollable_div
        )
        if overflow_y == 'auto':
            print("Found scrollable container using footer")
            return scrollable_div
    except Exception as e:
        print(f"Could not find scrollable div by footer: {str(e)}")
    return None

def get_scrollable_div_by_overflow(driver, element):
    """
    Recursively traverse up the DOM tree from the given element until finding
    a container with overflow-y: auto.
    
    :param driver: selenium webdriver
    :param element: starting element to search from
    :return: scrollable element or None if not found
    """
    try:
        max_iterations = 10  # Prevent infinite loops
        current = element
        
        for _ in range(max_iterations):
            if not current:
                break
                
            overflow_y = driver.execute_script(
                "return window.getComputedStyle(arguments[0]).getPropertyValue('overflow-y')", 
                current
            )
            
            if overflow_y == 'auto':
                print("Found scrollable container with overflow-y: auto")
                return current
                
            # Move up to parent
            try:
                current = current.find_element(By.XPATH, "./..")
            except:
                break
    except Exception as e:
        print(f"Error in recursive overflow check: {str(e)}")
    return None

def get_scrollable_div_by_scrollable(driver):
    """
    Find scrollable container by checking job card containers and their ancestors
    for overflow-y: auto property.
    
    :param driver: selenium webdriver
    :return: scrollable element or None if not found
    """
    try:
        job_cards = get_job_cards(driver)
        
        if job_cards:
            # Try with first job card
            scrollable = get_scrollable_div_by_overflow(driver, job_cards[0])
            if scrollable:
                print("Found scrollable container using overflow-y: auto")
                return scrollable
    except Exception as e:
        print(f"Could not find scrollable div by overflow: {str(e)}")
    return None

def scroll_jobs_list(driver):
    """
    LinkedIn specific function for loading all available jobs in the scrollable section of LinkedIn's
    jobs list.

    :param driver: selenium web driver
    :param el: parent element containing the job listings
    :return:
    """
    # Try different methods to find the scrollable container
    scrollable_div = None
    
    # Method 1: Try finding by footer
    scrollable_div = get_scrollable_div_by_footer(driver)
    
    # Method 2: Try finding by overflow-y property
    if not scrollable_div:
        scrollable_div = get_scrollable_div_by_scrollable(driver)
    
    # Fallback to provided element
    if not scrollable_div:
        print("PROBLEM: could not find scrollable element")
    
    # Get initial scroll height
    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
    print(f"Initial scroll height: {last_height}")
    
    scroll_attempts = 0
    max_attempts = 10  # Prevent infinite loops
    
    while scroll_attempts < max_attempts:
        # Scroll to bottom of scrollable div using JavaScript
        driver.execute_script("""
            arguments[0].scrollTo({
                top: arguments[0].scrollHeight,
                behavior: 'smooth'
            });
        """, scrollable_div)
        
        # Additional scroll to ensure we trigger the load
        time.sleep(0.5)
        driver.execute_script("arguments[0].scrollBy(0, 100);", scrollable_div)
        
        # Wait for content to load
        time.sleep(1)
        
        # Get new scroll height and job count
        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        current_jobs = len(get_job_cards(driver))
        print(f"New scroll height: {new_height}, Current job count: {current_jobs}")
        
        # Break if no new content or we have enough jobs
        if new_height == last_height or current_jobs >= 25:
            print("Reached end of scrolling")
            break
            
        last_height = new_height
        scroll_attempts += 1
    
    # Scroll back to top
    driver.execute_script("arguments[0].scrollTo(0, 0);", scrollable_div)
