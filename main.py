import functools

import urllib3
import requests
from serpapi import GoogleSearch
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from multiprocessing import Pool
import time
from dotenv import load_dotenv
import os
from urllib.parse import urlparse
import argparse
from rich.progress import Progress
from rich.console import Console
from pathvalidate import sanitize_filename

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def process_url(organic, screenshot_folder):
    driver = None
    try:
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")

        driver = webdriver.Firefox(options=options)

        url = organic.get('link')
        parsed = urlparse(url)
        hostname = str(parsed.hostname)
        base_url = parsed.scheme + "://" + hostname

        response = requests.get(url, verify=False, timeout=20)  # Set timeout to 20 seconds
        text = response.text

        driver.get(base_url)
        time.sleep(2)
        driver.save_screenshot(f"{screenshot_folder}/screenshot_{hostname}.png")

    except Exception as e:
        console = Console()
        error_message = f"Error processing URL {organic.get('link')}: {str(e)}"
        console.print(f"\n[bold red]{error_message}[/]")

    finally:
        if driver is not None:
            driver.quit()


def search_and_screenshot(search_phrase, limit):
    total_processed = 0  # Variable to keep track of the total processed results
    page = 1  # Start with page 1
    safe_phrase = sanitize_filename(search_phrase)[:200]
    datetime = time.strftime("%Y-%m-%d-%H%M%S")
    output_dir = f'output/{safe_phrase}/{datetime}'
    links_filename = f'{output_dir}/links.txt'
    screenshot_folder = f'{output_dir}/screenshots'

    while total_processed < limit:
        search = GoogleSearch({
            "q": search_phrase,
            "api_key": os.getenv("SERP_API_KEY"),
            "hl": "en",
            "start": (page - 1) * 10,  # Calculate the start index based on the page number
            "filter": "0"
        })

        result = search.get_dict()
        organics = result.get('organic_results', [])

        console = Console()
        console.print(f"Found {len(organics)} organic results for {search_phrase} (Page {page}): ")

        for organic in organics:
            console.print(f"{organic.get('position')}. {organic.get('link')}")

        if not os.path.exists(screenshot_folder):
            os.makedirs(screenshot_folder)

        with open(links_filename, "a+") as links_file:
            links_file.seek(0)
            existing_links = links_file.read().splitlines()
            for organic in organics:
                link = organic.get('link')
                if link not in existing_links:
                    links_file.write(f"{link}\n")

        with Progress() as progress:
            task = progress.add_task("[cyan]Processing URLs...", total=min(len(organics), limit - total_processed))
            with Pool() as p:
                process_url_partial = functools.partial(process_url, screenshot_folder=screenshot_folder)
                for _ in p.imap_unordered(process_url_partial, organics, chunksize=1):
                    progress.update(task, advance=1)
                    total_processed += 1

            progress.stop()

        page += 1  # Move to the next page

        if not organics or total_processed >= limit:
            break


if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Search and take screenshots')

    # Add the command line arguments
    parser.add_argument('search_phrase', type=str, help='The phrase to search for')
    parser.add_argument('--limit', type=int, default=5, help='The number of search results to process')

    # Parse the arguments
    args = parser.parse_args()

    # Run the function with the command line arguments
    search_and_screenshot(args.search_phrase, args.limit)
