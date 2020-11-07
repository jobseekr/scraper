import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# get env vars from python-dotenv
load_dotenv()

# defaults
start_url = "https://ca.indeed.com/browsejobs"
test_start_url = "https://ca.indeed.com/jobs?q=Software+Developer+%24123%2C000&l=Toronto%2C+ON&start=80"


def set_chrome_options(env: str) -> Options:
    chrome_options = Options()

    if env == "dev":
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--window-size=1920,1080")  # use this for debugging on Windows
    else:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")

    return chrome_options


def search_job(web_driver: WebDriver, what: str, where: str) -> None:
    """
    Searches Indeed for a particular job (what) for a particular location (where).
    """
    try:
        job_title_input = web_driver.find_element_by_id("what")
        location_input = web_driver.find_element_by_id("where")
        job_title_input.send_keys(what)
        location_input.send_keys(where)
        web_driver.find_element_by_id("fj").click()
    except Exception as err:
        print(f"Error Searching Job {what} in {where}: " + str(err))


def get_per_posting_info(web_driver: WebDriver, search_items: list) -> None:
    try:
        for title in search_items:
            WebDriverWait(web_driver, 5)
            title.find_element_by_xpath('..').click()
            info_container = WebDriverWait(web_driver, 10).until(
                EC.presence_of_element_located((By.ID, "vjs-container"))
            )
            print(info_container.find_element_by_id("vjs-jobinfo").text)
    except Exception as err:
        print(f"Error retrieving job info: " + str(err))


def has_next(web_driver: WebDriver) -> bool:
    """
    Check to see if next page exists
    """
    try:
        next_page = web_driver.find_element_by_xpath("//a[@aria-label='Next']")
        if next_page.size != 0:
            return True
    except Exception as err:
        print(f"Next page DNE: " + str(err))
        return False


def main() -> None:
    """
    Driver function
    """
    # initialize
    curr_page = 1
    pages_wanted = int(os.getenv("PAGES")) or None
    driver = webdriver.Chrome(os.getenv("WEBDRIVER_PATH"), options=set_chrome_options(os.getenv("ENVIRONMENT")))
    # driver.get(start_url)
    driver.get(test_start_url)
    # Main Search
    search_job(driver, "Software Developer", "Toronto, ON")
    driver.implicitly_wait(10)

    # Every job title in a page
    while has_next(driver) or (pages_wanted is not None and curr_page != pages_wanted):
        search_items_per_page = driver.find_elements_by_xpath("//a[@data-tn-element='jobTitle']")
        get_per_posting_info(driver, search_items_per_page)
        curr_page += 1


if __name__ == '__main__':
    main()
