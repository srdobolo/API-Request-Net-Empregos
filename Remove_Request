import requests
from bs4 import BeautifulSoup
import json
import html
from urllib.parse import urljoin, urlparse, urlunparse

# Base URL for the find-jobs section
BASE_URL = 'https://www.recruityard.com/find-jobs-all/'

# API endpoint and key
REMOVE_API_URL = "http://partner.net-empregos.com/hrsmart_remove.asp"
KEY_FILE_PATH = "API_ACCESS_KEY"

# Headers to mimic a browser request
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# Function to clean URLs and avoid duplicate segments
def clean_url(base, href):
    full_url = urljoin(base, href)
    parsed = urlparse(full_url)
    path_segments = parsed.path.split('/')
    # Keep only the first occurrence of 'find-jobs-all'
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
    response = requests.get(BASE_URL, headers=HEADERS)
    response.raise_for_status()  # Raise an error for bad HTTP responses
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
    print(f"Fetching job page: {job_url}")
    try:
        # Fetch the job details page
        response = requests.get(job_url, headers=HEADERS)
        response.raise_for_status()
        job_html_content = response.content

        # Parse the HTML with BeautifulSoup
        job_soup = BeautifulSoup(job_html_content, 'html.parser')

        # Locate the <script> tag containing the JSON
        script_tag = job_soup.find('script', type='application/ld+json')

        if script_tag and script_tag.string:
            json_content = script_tag.string

            try:
                # Unescape and parse the JSON content
                json_content_unescaped = html.unescape(json_content)
                data = json.loads(json_content_unescaped)

                # Prepare and send the removal request
                remove_payload = {
                    "ACCESS": API_KEY,
                    "REF": data.get('identifier', {}).get('value', 'job001'),
                }

                try:
                    remove_response = requests.get(REMOVE_API_URL, params=remove_payload)
                    if remove_response.status_code == 200:
                        print(f"Job '{remove_payload['REF']}' successfully removed.")
                    else:
                        print(f"Failed to remove job '{remove_payload['REF']}'. HTTP Status: {remove_response.status_code}")
                        print("Response Content:", remove_response.text)
                except requests.RequestException as e:
                    print(f"Error removing job '{remove_payload['REF']}': {e}")
                    continue

            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from the script tag at {job_url}.")
            except Exception as e:
                print(f"Unexpected error processing job at {job_url}: {e}")
        else:
            print(f"No JSON script tag found at {job_url}.")

    except requests.RequestException as e:
        print(f"Error fetching job URL {job_url}: {e}")

print("Processing complete.")