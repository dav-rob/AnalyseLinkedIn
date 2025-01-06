from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json

chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get("https://www.linkedin.com")

# Wait for manual login
input("Please log in to LinkedIn and then press Enter here...")

# Extract cookies
cookies = driver.get_cookies()
driver.quit()

# Save cookies to a file
with open('cookies/linkedin_cookies.json', 'w') as f:
    json.dump(cookies, f)
