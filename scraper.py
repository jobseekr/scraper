"""
Author: Kanisk Chakraborty - https://github.com/chakrakan/
Indeed Scraper v1.0

Scrape jobs off of Canadian Indeed
"""

from datetime import datetime, timedelta
from os import path, getenv, remove
import logging
import glob

from dotenv import load_dotenv
from selenium import webdriver
from time import sleep
from pathlib import Path

from selenium.common.exceptions import StaleElementReferenceException
from tqdm import tqdm
import pandas as pd
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from job import Job
import random

load_dotenv()
start_url = "https://ca.indeed.com/browsejobs"


def set_chrome_options(env: str) -> Options:
    """
    Method to set up Webdriver with Chrome options
    :param env: environment being run in dev/prod etc.
    :return: Options object for Chrome webdriver
    """
    chrome_options = Options()

    if env == "dev":
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--window-size=1920,1080")  # use this for debugging on Windows
    else:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")

    return chrome_options


def search_job(what: str, where: str) -> WebDriver:
    """
    Searches Indeed for a particular job (what) for a particular location (where).
    :param what: The job user queries for
    :param where: The location user queries for
    :return:
    """
    try:
        driver = webdriver.Chrome(getenv("WEBDRIVER_PATH"), options=set_chrome_options(getenv("ENVIRONMENT")))
        driver.get(start_url)
        job_title_input = driver.find_element_by_id("what")
        location_input = driver.find_element_by_id("where")
        job_title_input.send_keys(what)
        location_input.send_keys(where)
        driver.find_element_by_id("fj").click()
        driver.implicitly_wait(10)
        return driver
    except Exception as err:
        print(f"Error Searching Job {what} in {where}: " + str(err))


def get_per_page_info(web_driver: WebDriver, search_items: list) -> list:
    """
    Indeed jobs are paginated based on window size. Keeping 1980x1800 driver resolution
    we get roughly 15 items per page. Returns a list of job dicts to be used directly with
    a pandas Data-frame
    :param web_driver: Selenium driver object
    :param search_items: list of web elements found by selenium once a search is performed with user query
    :return: list of job dicts
    """
    try:
        jobs = []
        for title in tqdm(search_items):
            title.find_element_by_xpath('..').click()
            job_container = WebDriverWait(web_driver, 5).until(
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
            jobs.append(a_job.as_dict())
            sleep(random.randint(2, 4))
        return jobs
    except Exception as err:
        print(f"Error retrieving job info: " + str(err))


def has_next(web_driver: WebDriver) -> tuple:
    """
    Check to see if next page exists. If it does, navigate to it.
    :param web_driver: Selenium webdriver object
    :return: True/False based on next page condition
    """
    try:
        popup_handler(web_driver)
        next_page = web_driver.find_element_by_xpath("//a[@aria-label='Next']")
        if next_page.size != 0:
            return True, next_page
    except Exception as err:
        print(f"\nReached end of pagination. {err}")
        return False, None


def popup_handler(web_driver: WebDriver) -> None:
    """
    A method to handle pesky popups that come up during a scraping job on indeed
    :param web_driver:
    :return:
    """
    try:
        # check if there's a popup upon hitting the new page
        popup_container = WebDriverWait(web_driver, 10).until(
            EC.presence_of_element_located((By.ID, "popover-foreground"))
        )
        # if there is, close it and continue as usual
        if popup_container.size != 0:
            popup_container.find_element_by_xpath("//button[@aria-label='Close']").click()
    except Exception as err:
        print(f"\nPopup Handler {err}")


def save_run_data(total_jobs: list, pages_wanted: int, pages_got: int, job: str, location: str) -> str:
    """
    Save scraped jobs from a particular run to minimize repeated scrapes.
    :param pages_got:
    :param location:
    :param job:
    :param total_jobs:
    :param pages_wanted:
    :return:
    """
    # create data folder
    Path(f"data/{job.strip().lower()}-{location.strip().lower()}").mkdir(parents=True, exist_ok=True)
    file_path = Path(f"data/{job.strip().lower()}-{location.strip().lower()}")
    # create df from data
    jobs_df = pd.DataFrame(total_jobs)

    # naming convention
    file = ""
    # if requested is less than actual pages got, then clearly we have hit the maximal pages that query can ever return
    # so we tag that file, and for loading we can query based on if a file begins with max
    if pages_wanted > pages_got:
        file += "maxscrape"
    else:
        file += "scrape"
    file += datetime.now().strftime("_%d-%m-%Y_%H-%M-%S")
    file += f"_{pages_got}-pgs"

    full_file_path = file_path / file

    # save as a serialized pickle file
    jobs_df.to_pickle(full_file_path)
    print(f"Saved data into {full_file_path}\n")
    return full_file_path


def read_last_run(job: str, location: str, pages_wanted: int) -> str:
    """
    Checks the "data" folder to find latest data output from previous runs.
    :return: string path to the latest created file based on recency/optimal needs
    """
    existing_files = glob.glob(f"data/{job.strip().lower()}-{location.strip().lower()}/*")
    latest_file = None
    if existing_files:
        print("Found previous runs, preloading most recent/optimal data...\n")
        max_pgs_scraped = 0
        for file in existing_files:
            curr_file_pgs = int(file.split('_')[3].split('-')[0])
            if max_pgs_scraped < curr_file_pgs:
                max_pgs_scraped = curr_file_pgs
                latest_file = file

        # check to see if all data was recently acquired (~ 10 hours)
        latest_file_datetime = datetime.fromtimestamp(path.getctime(latest_file))
        print(f"Max pages scraped is {max_pgs_scraped} on {latest_file_datetime}\n")
        check_date = datetime.now() - timedelta(hours=20)

        if latest_file.split('/')[2].startswith('scrape') and max_pgs_scraped < pages_wanted:
            print(f"Requested more pages than maximum scraped till date {max_pgs_scraped}\n")
            latest_file = None

        # if date of creation of our data is older than 10 hours from present, get fresh data
        if latest_file_datetime < check_date:
            print("Data is stale, fetching new data...\n")
            latest_file = None

        # also automatically purge older data files
        if len(existing_files) > 5:
            print("Cleaning up and removing some older/unused files...\n")
            oldest_file = min(existing_files, key=path.getctime)
            remove(oldest_file)

    return latest_file


def load_jobs_from_file(file_path: str) -> pd.DataFrame:
    """
    Read pickle file and create a pandas data-frame to be used
    :param file_path: path to pickle file
    :return:
    """
    job_df = pd.read_pickle(file_path)
    return job_df


def searchable_items(web_driver: WebDriver) -> list:
    """
    Finds list of searchable web element items to interact with in order to grab description data
    :param web_driver:
    :return:
    """
    # check if any popover elements are up and close them
    # otherwise retrieve all searchable links
    try:
        # first check of any pesky popovers and close them
        popup_handler(web_driver)
        # then attempt to populate search results

        search_results = web_driver.find_elements_by_xpath("//a[@data-tn-element='jobTitle']")
        if search_results:
            return search_results
    except Exception as err:
        print(f"\nCould not find job-titles from search " + str(err))


def scrape_jobs(job: str, location: str, total_pages: int) -> tuple:
    """
    Call the webdriver and start the scraping process for fresh batch of job data
    :return: tuple of list of jobs and total pages to scrape provided by user
    """
    # initialize
    all_jobs = []
    max_actual_pages = None

    # Main Search
    driver = search_job(job, location)

    # Every job title in a page
    for curr_page in range(0, total_pages):
        start_time = datetime.now()
        print(f"\nGathering data from page {curr_page + 1} of {total_pages}...\n")
        search_results = searchable_items(driver)
        all_jobs.extend(get_per_page_info(driver, search_results))
        has_next_page, next_locator = has_next(driver)
        elapsed_time = datetime.now() - start_time
        logging.info(f"Page {curr_page + 1} done in {elapsed_time.total_seconds()}s")
        max_actual_pages = curr_page + 1
        if has_next_page:
            next_locator.click()
            continue
        else:
            break

    driver.quit()

    return all_jobs, total_pages, max_actual_pages


def initialize(job: str, location: str, pages: int = 120) -> pd.DataFrame:
    """
    Driver function
    """
    # init
    jobs_df = None
    logging.disable(True)
    pages_to_scrape = int(getenv("PAGES") or pages)
    # if prev runs exist, load data instead of scraping
    latest_file_path = read_last_run(job, location, pages_to_scrape)

    if latest_file_path is not None:
        jobs_df = load_jobs_from_file(latest_file_path)
    else:
        # set logging
        log_file = f"logs/run-{datetime.now()}.log"
        logging.basicConfig(filename=log_file, level=logging.INFO)
        # run scraper and destructure out data for other functions
        all_jobs, pages_wanted, pages_actual = scrape_jobs(job, location, pages_to_scrape)
        # save all data from a run
        data_file = save_run_data(all_jobs, pages_wanted, pages_actual, job, location)
        jobs_df = load_jobs_from_file(data_file)

    return jobs_df


# if run standalone, it will try to scrape 2 pages of Software Development Jobs
# in Toronto, ON as a demo, and print out the dataframe to console
if __name__ == '__main__':
    print(initialize("Software Developer", "Toronto, ON"))
    # print(load_jobs_from_file("data/software developer-toronto, on/scrape_13-11-2020_15-33-13_100-pgs")[
    # "job_description"][1])
