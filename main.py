import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from serpapi import GoogleSearch
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from multiprocessing import Pool
import time
from dotenv import load_dotenv
import os
from urllib.parse import urlparse
import argparse
from rich.progress import Progress, TaskID

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def process_url(organic):
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        webdriver_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

        url = organic.get('link')
        parsed = urlparse(url)
        hostname = str(parsed.hostname)
        base_url = parsed.scheme + "://" + hostname

        response = requests.get(url, verify=False, timeout=20)  # Set timeout to 20 seconds
        text = response.text

        driver.get(base_url)
        time.sleep(2)
        driver.save_screenshot(f"screenshots/screenshot_{hostname}.png")

    except Exception as e:
        print(f"Error processing URL {organic.get('link')}: {str(e)}")
    finally:
        if driver is not None:
            driver.quit()


def search_and_screenshot(search_phrase, num_results):
    search = GoogleSearch({
        "q": search_phrase,
        "num": num_results,
        "api_key": os.getenv("SERP_API_KEY")
    })

    result = search.get_dict()

    organics = result.get('organic_results', [])

    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')

    with open("links.txt", "a+") as links_file:
        links_file.seek(0)
        existing_links = links_file.read().splitlines()

        with Progress() as progress:
            task = progress.add_task("[cyan]Processing URLs...", total=len(organics))
            with Pool() as p:
                for _ in p.imap_unordered(process_url, organics, chunksize=1):
                    progress.update(task, advance=1)

            progress.stop()


if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Search and take screenshots')

    # Add the command line arguments
    parser.add_argument('search_phrase', type=str, help='The phrase to search for')
    parser.add_argument('--num_results', type=int, default=5, help='The number of search results to process')

    # Parse the arguments
    args = parser.parse_args()

    # Run the function with the command line arguments
    search_and_screenshot(args.search_phrase, args.num_results)
