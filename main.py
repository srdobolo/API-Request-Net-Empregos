import requests
from bs4 import BeautifulSoup
import json
import html
from urllib.parse import urljoin, urlparse, urlunparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from data_cleaning import clean_job_data  # Updated function below

# Base URL and API endpoints
BASE_URL = 'https://www.recruityard.com/find-jobs-all/'
API_URL = "http://partner.net-empregos.com/hrsmart_insert.asp"
REMOVE_API_URL = "http://partner.net-empregos.com/hrsmart_remove.asp"
KEY_FILE_PATH = "API_ACCESS_KEY"
MAPPING_FILE_PATH = "mapping.json"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# Set up session with retries
session = requests.Session()
retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

successful_requests = 0
failed_jobs = []

# Function to clean URLs
def clean_url(base, href):
    full_url = urljoin(base, href)
    parsed = urlparse(full_url)
    path_segments = parsed.path.split('/')
    cleaned_path = '/'.join([seg for i, seg in enumerate(path_segments) if seg != 'find-jobs-all' or i == path_segments.index('find-jobs-all')])
    return urlunparse((parsed.scheme, parsed.netloc, cleaned_path, parsed.params, parsed.query, parsed.fragment))

# Function to convert HTML to minimalist HTML
def simplify_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    for element in soup(['script', 'style']):
        element.decompose()
    lines = []
    for element in soup.recursiveChildGenerator():
        if isinstance(element, str):
            text = element.strip()
            if text:
                lines.append(text)
        elif element.name in ['br', 'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            lines.append('')
    result = ''
    prev_empty = False
    for line in lines:
        if line:
            result += line + '<br>'
            prev_empty = False
        elif not prev_empty:
            result += '<br>'
            prev_empty = True
    if result.endswith('<br>'):
        result = result[:-4]
    return result

# Function to format REF to 20 alphanumeric characters
def format_ref(ref):
    cleaned_ref = ''.join(c for c in str(ref) if c.isalnum())
    if len(cleaned_ref) < 20:
        cleaned_ref = cleaned_ref.ljust(20, '0')
    elif len(cleaned_ref) > 20:
        cleaned_ref = cleaned_ref[:20]
    return cleaned_ref

# Read API key
try:
    with open(KEY_FILE_PATH, "r") as file:
        API_KEY = file.read().strip()
except FileNotFoundError:
    print(f"Error: '{KEY_FILE_PATH}' not found.")
    exit(1)

# Load mapping file
try:
    with open(MAPPING_FILE_PATH, "r", encoding="iso-8859-1") as file:
        mappings = json.load(file)
except FileNotFoundError:
    print(f"Error: '{MAPPING_FILE_PATH}' not found.")
    exit(1)
except json.JSONDecodeError as e:
    print(f"Error: Failed to parse '{MAPPING_FILE_PATH}': {e}")
    exit(1)

# Fetch main jobs page
try:
    print(f"Fetching base URL: {BASE_URL}")
    response = session.get(BASE_URL, headers=HEADERS, timeout=10)
    response.raise_for_status()
    html_content = response.content
except requests.RequestException as e:
    print(f"Error fetching base URL: {e}")
    exit(1)

# Parse HTML to find job links
soup = BeautifulSoup(html_content, 'html.parser')
all_hrefs = [a['href'] for a in soup.find_all('a', href=True)]
print("All hrefs on page:", all_hrefs)

job_links = list(set([
    clean_url(BASE_URL, a['href']) for a in soup.find_all('a', href=True)
    if '/find-jobs-all/' in a['href'] and a['href'].endswith('pt')
]))
print(f"Found {len(job_links)} job(s) to process ending with 'pt': {job_links}")

# Process jobs
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

                formatted_description, zona, categoria, tipo = clean_job_data(data, mappings)
                minimalist_description = simplify_html(formatted_description)

                # Debug categoria mapping
                print(f"Category after cleaning: {data.get('industry', {}).get('value', 'Unknown')} -> {categoria}")

                raw_ref = data.get('identifier', {}).get('value', 'job001')
                formatted_ref = format_ref(raw_ref)
                print(f"Raw REF: {raw_ref} -> Formatted REF: {formatted_ref}")

                payload = {
                    "ACCESS": API_KEY,
                    "REF": formatted_ref,
                    "TITULO": data.get('title', 'undisclosed'),
                    "TEXTO": (
                        f"{minimalist_description}<br><br>"
                        f"<a href=\"{job_url}?id={formatted_ref}&utm_source=NET_EMPREGOS\" target=\"_blank\">Clique aqui para se candidatar!</a><br>"
                        f"ou por email para info@recruityard.com"
                    ),
                    "ZONA": zona,
                    "CATEGORIA": categoria,
                    "TIPO": tipo,
                }
                encoded_payload = {
                    key: (value.encode('iso-8859-1', errors='replace') if isinstance(value, str) else value)
                    for key, value in payload.items()
                }
                remove_payload = {
                    "ACCESS": API_KEY,
                    "REF": formatted_ref,
                }

                # Remove job
                for attempt in range(3):
                    try:
                        remove_response = session.get(REMOVE_API_URL, params=remove_payload, timeout=10)
                        print(f"Remove response for '{remove_payload['REF']}': {remove_response.status_code} - {remove_response.text}")
                        if remove_response.status_code == 200:
                            print(f"Job '{remove_payload['REF']}' successfully removed.")
                            break
                        else:
                            print(f"Failed to remove job '{remove_payload['REF']}': {remove_response.status_code}")
                            if attempt < 2:
                                time.sleep(2)
                    except requests.RequestException as e:
                        print(f"Error removing job '{remove_payload['REF']}': {e}")
                        if attempt < 2:
                            time.sleep(2)
                else:
                    print(f"Failed to remove '{remove_payload['REF']}' after 3 attempts.")

                # Post job
                for attempt in range(3):
                    try:
                        post_response = session.post(API_URL, data=encoded_payload, timeout=10)
                        print(f"Post response for '{payload['TITULO']}': {post_response.status_code} - {post_response.text}")
                        if post_response.status_code == 200 and "Error" not in post_response.text:
                            print(f"Job '{payload['TITULO']}' successfully posted.")
                            successful_requests += 1
                            break
                        else:
                            print(f"Failed to post job '{payload['TITULO']}': {post_response.status_code} - {post_response.text}")
                            if attempt < 2:
                                time.sleep(2)
                    except requests.RequestException as e:
                        print(f"Error posting job '{payload['TITULO']}': {e}")
                        if attempt < 2:
                            time.sleep(2)
                else:
                    print(f"Failed to post '{payload['TITULO']}' after 3 attempts.")
                    failed_jobs.append((job_url, payload['TITULO'], post_response.text if 'post_response' in locals() else "Unknown error"))

            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON at {job_url}.")
                failed_jobs.append((job_url, "Unknown", "JSON decode error"))
            except Exception as e:
                print(f"Unexpected error processing job at {job_url}: {e}")
                failed_jobs.append((job_url, "Unknown", str(e)))
        else:
            print(f"No JSON script tag found at {job_url}.")
            failed_jobs.append((job_url, "Unknown", "No JSON data"))

    except requests.RequestException as e:
        print(f"Error fetching job URL {job_url}: {e}")
        failed_jobs.append((job_url, "Unknown", str(e)))

    time.sleep(1)

print("\nProcessing complete.")
print(f"Total number of job requests successfully posted: {successful_requests}/{len(job_links)}")
if failed_jobs:
    print("\nFailed jobs:")
    for url, title, reason in failed_jobs:
        print(f"- {title} ({url}): {reason}")
print("\nWaiting 60 seconds to check for website update...")
time.sleep(60)
print("Check the website now to confirm postings.")