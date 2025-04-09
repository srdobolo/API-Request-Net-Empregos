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

successful_removals = 0  # Renamed for clarity
failed_removals = []    # Track failed removals

# Function to clean URLs and avoid duplicate segments
def clean_url(base, href):
    full_url = urljoin(base, href)
    parsed = urlparse(full_url)
    path_segments = parsed.path.split('/')
    cleaned_path = '/'.join([seg for i, seg in enumerate(path_segments) if seg != 'find-jobs-all' or i == path_segments.index('find-jobs-all')])
    return urlunparse((parsed.scheme, parsed.netloc, cleaned_path, parsed.params, parsed.query, parsed.fragment))

# Function to format REF to 20 alphanumeric characters
def format_ref(ref):
    cleaned_ref = ''.join(c for c in str(ref) if c.isalnum())
    if len(cleaned_ref) < 20:
        cleaned_ref = cleaned_ref.ljust(20, '0')
    elif len(cleaned_ref) > 20:
        cleaned_ref = cleaned_ref[:20]
    return cleaned_ref

# Read the API key
try:
    with open(KEY_FILE_PATH, "r") as file:
        API_KEY = file.read().strip()
except FileNotFoundError:
    print(f"Error: '{KEY_FILE_PATH}' not found.")
    exit(1)

# Step 1: Load the main jobs page to find all job links
try:
    print(f"Fetching base URL: {BASE_URL}")
    response = session.get(BASE_URL, headers=HEADERS, timeout=10)
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
for job_url in job_links:
    print(f"\nFetching job page: {job_url}")
    try:
        response = session.get(job_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        job_html_content = response.content

        job_soup = BeautifulSoup(job_html_content, 'html.parser')
        script_tag = job_soup.find('script', type='application/ld+json')

        if script_tag and script_tag.string:
            json_content = script_tag.string

            try:
                json_content_unescaped = html.unescape(json_content)
                data = json.loads(json_content_unescaped)

                raw_ref = data.get('identifier', {}).get('value', 'job001')
                formatted_ref = format_ref(raw_ref)
                print(f"Raw REF: {raw_ref} -> Formatted REF: {formatted_ref}")

                remove_payload = {
                    "ACCESS": API_KEY,
                    "REF": formatted_ref,
                }

                # Retry logic for removal request
                for attempt in range(3):
                    try:
                        remove_response = session.get(REMOVE_API_URL, params=remove_payload, timeout=10)
                        print(f"Remove response for '{formatted_ref}': {remove_response.status_code} - {remove_response.text}")
                        if remove_response.status_code == 200:
                            print(f"Job '{formatted_ref}' successfully removed.")
                            successful_removals += 1
                            break
                        else:
                            print(f"Attempt {attempt + 1}: Failed to remove job '{formatted_ref}': {remove_response.status_code} - {remove_response.text}")
                            if attempt < 2:
                                time.sleep(2)
                    except requests.RequestException as e:
                        print(f"Attempt {attempt + 1}: Error removing job '{formatted_ref}': {e}")
                        if attempt < 2:
                            time.sleep(2)
                else:
                    print(f"Failed to remove '{formatted_ref}' after 3 attempts.")
                    failed_removals.append((job_url, formatted_ref, remove_response.text if 'remove_response' in locals() else "Unknown error"))

            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from the script tag at {job_url}.")
                failed_removals.append((job_url, "Unknown", "JSON decode error"))
            except Exception as e:
                print(f"Unexpected error processing job at {job_url}: {e}")
                failed_removals.append((job_url, "Unknown", str(e)))
        else:
            print(f"No JSON script tag found at {job_url}.")
            failed_removals.append((job_url, "Unknown", "No JSON data"))

    except requests.RequestException as e:
        print(f"Error fetching job URL {job_url}: {e}")
        failed_removals.append((job_url, "Unknown", str(e)))

    time.sleep(5)  # Delay of 5 seconds between job requests

print("\nProcessing complete.")
print(f"Total jobs successfully removed: {successful_removals}/{len(job_links)}")
if failed_removals:
    print("\nFailed removals:")
    for url, ref, reason in failed_removals:
        print(f"- {ref} ({url}): {reason}")