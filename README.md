# Search and Screenshot Tool

This is a Python script that utilizes Selenium WebDriver, BeautifulSoup, and SerpAPI to search a specified phrase on Google, scrape the resulting links, and take screenshots of these webpages.

## Prerequisites

Before running the script, you need to install the required Python packages. You can do so using pip:

"""
pip install -r requirements.txt
"""

The required packages include:

- serpapi
- requests
- beautifulsoup4
- selenium
- webdriver_manager
- python-dotenv

## Setting Up

1. Clone this repository:

"""
git clone https://github.com/yourusername/search-and-screenshot.git
cd search-and-screenshot
"""

2. Create a .env file in the root directory of the project and add your SerpAPI key like so:

"""
SERP_API_KEY=your_serpapi_key_here
"""

Make sure to replace `your_serpapi_key_here` with your actual SerpAPI key.

## Usage

You can run the script using the command line. It takes a search phrase as a required argument and the number of search results to process as an optional argument. If the number of results is not specified, it defaults to 5.

Here's an example:

"""
python main.py "OpenAI" --num_results 10
"""

In this example, "OpenAI" is the search phrase and 10 is the number of search results to process. If you leave out `--num_results`, the script will default to processing 5 search results.

## Output

The script will save the screenshots in the `screenshots` folder in the root directory of the project. It will also save the processed URLs in a file named `links.txt` to ensure that each URL is processed only once. 

## Contributing

If you have suggestions for how this script could be improved, please open an issue or submit a pull request!

## License

This project is licensed under the terms of the MIT license.
