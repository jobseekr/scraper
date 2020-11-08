import os

from dotenv import load_dotenv
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from job import Job
import random

# get env vars from python-dotenv
load_dotenv()

# defaults
start_url = "https://ca.indeed.com/browsejobs"


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


def get_per_page_info(web_driver: WebDriver, search_items: list) -> list:
    try:
        jobs = []
        for title in search_items:
            title.find_element_by_xpath('..').click()
            job_container = WebDriverWait(web_driver, 15).until(
                EC.presence_of_element_located((By.ID, "vjs-container"))
            )
            info_container = job_container.find_element_by_id("vjs-jobinfo")
            job_title = info_container.find_element_by_id("vjs-jobtitle").text
            job_cp = info_container.find_element_by_id("vjs-cn").text
            job_loc = info_container.find_element_by_id("vjs-loc").text
            job_desc = job_container.find_element_by_id("vjs-desc").text

            full_chunk = str(info_container.text)

            # create new Job object
            a_job = Job(job_title, job_cp, job_loc, job_desc, full_chunk)
            print(a_job.get_overview() + "\n")
            jobs.append(a_job)
            sleep(3 + random.randint(0, 2))
        return jobs
    except Exception as err:
        print(f"Error retrieving job info: " + str(err))


def has_next(web_driver: WebDriver) -> bool:
    """
    Check to see if next page exists. If it does, navigate to it.
    """
    try:
        next_page = web_driver.find_element_by_xpath("//a[@aria-label='Next']")
        if next_page.size != 0:
            next_page.click()
            popup_container = WebDriverWait(web_driver, 10).until(
                EC.presence_of_element_located((By.ID, "popover-foreground"))
            )
            popup_container.find_element_by_xpath("//button[@aria-label='Close']").click()
            return True
    except Exception as err:
        print(f"Reached end of pagination. " + str(err))
        return False


def main() -> None:
    """
    Driver function
    """
    # initialize
    paginated_jobs = {}
    pages_wanted = int(os.getenv("PAGES")) or 100
    driver = webdriver.Chrome(os.getenv("WEBDRIVER_PATH"), options=set_chrome_options(os.getenv("ENVIRONMENT")))
    driver.get(start_url)

    # Main Search
    search_job(driver, "Software Developer", "Toronto, ON")
    driver.implicitly_wait(10)

    # Every job title in a page
    for curr_page in range(0, pages_wanted):
        print(f"Gathering data from page {curr_page + 1} of {pages_wanted}...\n")
        search_items_per_page = driver.find_elements_by_xpath("//a[@data-tn-element='jobTitle']")
        paginated_jobs[curr_page] = get_per_page_info(driver, search_items_per_page)
        print(f"\n############# {curr_page + 1} #############")
        if not has_next(driver):
            break

    print(paginated_jobs)


if __name__ == '__main__':
    main()
