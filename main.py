from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
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

load_dotenv()


def process_url(organic):
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    webdriver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    url = organic.get('link')
    parsed = urlparse(url)
    hostname = str(parsed.hostname)
    base_url = parsed.scheme + "://" + hostname

    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')

    search_phrase = organic.get('title')

    if search_phrase.lower() in soup.get_text().lower():
        driver.get(base_url)
        time.sleep(2)
        driver.save_screenshot(f"screenshots/screenshot_{hostname}.png")

    driver.quit()


def search_and_screenshot(search_phrase, num_results):
    search = GoogleSearch({
        "q": search_phrase,
        "num": num_results,
        "api_key": os.getenv("SERP_API_KEY")
    })

    result = search.get_dict()
    print(len(result))

    organics = result.get('organic_results', [])

    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')

    with open("links.txt", "a+") as links_file:
        links_file.seek(0)
        existing_links = links_file.read().splitlines()

        for i, organic in enumerate(organics, start=1):
            url = organic.get('link')
            if url not in existing_links:
                links_file.write(url + '\n')

        with Pool() as p:
            p.map(process_url, organics)


# Create an argument parser
parser = argparse.ArgumentParser(description='Search and take screenshots')

# Add the command line arguments
parser.add_argument('search_phrase', type=str, help='The phrase to search for')
parser.add_argument('--num_results', type=int, default=5, help='The number of search results to process')

# Parse the arguments
args = parser.parse_args()

# Run the function with the command line arguments
search_and_screenshot(args.search_phrase, args.num_results)
