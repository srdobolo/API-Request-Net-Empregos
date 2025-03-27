import requests
from bs4 import BeautifulSoup
import json
import html
from urllib.parse import urljoin, urlparse, urlunparse
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Base URL for the find-jobs section
BASE_URL = 'https://www.recruityard.com/find-jobs-all/'

# API endpoint and key
REMOVE_API_URL = "http://partner.net-empregos.com/hrsmart_remove.asp"
KEY_FILE_PATH = "API_ACCESS_KEY"

# Headers to mimic a browser request
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# Set up a session with retry logic
session = requests.Session()
retry_strategy = Retry(
    total=3,  # Retry up to 3 times
    backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
    status_forcelist=[429, 500, 502, 503, 504]  # Retry on these HTTP status codes
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Function to clean URLs and avoid duplicate segments
def clean_url(base, href):
    full_url = urljoin(base, href)
    parsed = urlparse(full_url)
    path_segments = parsed.path.split('/')
    cleaned_path = '/'.join([seg for i, seg in enumerate(path_segments) if seg != 'find-jobs-all' or i == path_segments.index('find-jobs-all')])
    return urlunparse((parsed.scheme, parsed.netloc, cleaned_path, parsed.params, parsed.query, parsed.fragment))

# Read the API key
try:
    with open(KEY_FILE_PATH, "r") as file:
        API_KEY = file.read().strip()
except FileNotFoundError:
    print(f"Error: The file '{KEY_FILE_PATH}' was not found. Please ensure it exists.")
    exit(1)

# Step 1: Load the main jobs page to find all job links
try:
    print(f"Fetching base URL: {BASE_URL}")
    response = session.get(BASE_URL, headers=HEADERS)
    response.raise_for_status()
    html_content = response.content
except requests.RequestException as e:
    print(f"Error fetching base URL: {e}")
    exit(1)

# Step 2: Parse the HTML with BeautifulSoup to find all job links
soup = BeautifulSoup(html_content, 'html.parser')

# Debug: Print all hrefs for inspection
all_hrefs = [a['href'] for a in soup.find_all('a', href=True)]
print("All hrefs on page:", all_hrefs)

# Extract job links, deduplicate, and filter those ending with "pt"
job_links = list(set([
    clean_url(BASE_URL, a['href']) for a in soup.find_all('a', href=True)
    if '/find-jobs-all/' in a['href'] and a['href'].endswith('pt')
]))

print(f"Found {len(job_links)} job(s) to process ending with 'pt': {job_links}")

# Step 3: Process each job link
removed_jobs = 0
for job_url in job_links:
    print(f"\nFetching job page: {job_url}")
    try:
        response = session.get(job_url, headers=HEADERS)
        response.raise_for_status()
        job_html_content = response.content

        job_soup = BeautifulSoup(job_html_content, 'html.parser')
        script_tag = job_soup.find('script', type='application/ld+json')

        if script_tag and script_tag.string:
            json_content = script_tag.string

            try:
                json_content_unescaped = html.unescape(json_content)
                data = json.loads(json_content_unescaped)

                ref_value = data.get('identifier', {}).get('value', 'job001')
                print(f"Extracted REF: {ref_value}")

                remove_payload = {
                    "ACCESS": API_KEY,
                    "REF": ref_value,
                }

                # Retry logic for removal request
                for attempt in range(3):
                    try:
                        remove_response = session.get(REMOVE_API_URL, params=remove_payload, timeout=10)
                        if remove_response.status_code == 200:
                            print(f"Job '{ref_value}' successfully removed.")
                            removed_jobs += 1
                            break
                        else:
                            print(f"Attempt {attempt + 1}: Failed to remove job '{ref_value}'. HTTP Status: {remove_response.status_code}")
                            print("Response Content:", remove_response.text)
                            if attempt < 2:
                                time.sleep(2)  # Wait before retrying
                    except requests.RequestException as e:
                        print(f"Attempt {attempt + 1}: Error removing job '{ref_value}': {e}")
                        if attempt < 2:
                            time.sleep(2)  # Wait before retrying
                else:
                    print(f"Failed to remove job '{ref_value}' after 3 attempts.")

            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from the script tag at {job_url}.")
            except Exception as e:
                print(f"Unexpected error processing job at {job_url}: {e}")
        else:
            print(f"No JSON script tag found at {job_url}.")

    except requests.RequestException as e:
        print(f"Error fetching job URL {job_url}: {e}")

    time.sleep(1)  # Small delay between job requests to avoid overwhelming the API

print("\nProcessing complete.")
print(f"Total jobs successfully removed: {removed_jobs}/{len(job_links)}")