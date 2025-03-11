import requests
from bs4 import BeautifulSoup
import json
import html
from urllib.parse import urljoin
from data_cleaning import clean_job_data  # Assuming you have this function implemented

# Base URL for the find-jobs section
BASE_URL = 'https://www.recruityard.com/'

# API endpoint and key
API_URL = "http://partner.net-empregos.com/hrsmart_insert.asp"
REMOVE_API_URL = "http://partner.net-empregos.com/hrsmart_remove.asp"
KEY_FILE_PATH = "API_ACCESS_KEY"
MAPPING_FILE_PATH = "mapping.json"

# Read the API key
try:
    with open(KEY_FILE_PATH, "r") as file:
        API_KEY = file.read().strip()
except FileNotFoundError:
    print(f"Error: The file '{KEY_FILE_PATH}' was not found. Please ensure it exists.")
    exit(1)

# Load the mapping file
try:
    with open(MAPPING_FILE_PATH, "r", encoding="iso-8859-1") as file:
        mappings = json.load(file)
except FileNotFoundError:
    print(f"Error: The file '{MAPPING_FILE_PATH}' was not found. Please ensure it exists.")
    exit(1)
except json.JSONDecodeError as e:
    print(f"Error: Failed to parse '{MAPPING_FILE_PATH}': {e}")
    exit(1)

# Step 1: Load the main jobs page to find all job links
try:
    response = requests.get(BASE_URL)
    response.raise_for_status()  # Raise an error for bad HTTP responses
    html_content = response.content
except requests.RequestException as e:
    print(f"Error fetching base URL: {e}")
    exit(1)

# Step 2: Parse the HTML with BeautifulSoup to find all job links
soup = BeautifulSoup(html_content, 'html.parser')

# Extract job links, deduplicate, and filter those ending with "pt"
job_links = list(set([
    urljoin(BASE_URL, a['href']) for a in soup.find_all('a', href=True)
    if '/find-jobs-all/' in a['href'] and a['href'].endswith('pt')
]))

print(f"Found {len(job_links)} job(s) to process ending with 'pt'.")

# Step 3: Process each job link
for job_url in job_links:
    try:
        # Fetch the job details page
        response = requests.get(job_url)
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

                # Clean the job data
                formatted_description, zona, categoria, tipo = clean_job_data(data, mappings)

                # Prepare the payload for the API request
                payload = {
                    "ACCESS": API_KEY,
                    "REF": data.get('identifier', {}).get('value', 'job001'),
                    "TITULO": data.get('title', 'undisclosed'),
                    "TEXTO": (
                        f"{formatted_description}\n\n"
                        f'<a href="{job_url}" target="_blank">Clique aqui para se candidatar!</a> '
                        "ou por email para info@smart-recruitments.com"
                    ),
                    "ZONA": zona,
                    "CATEGORIA": categoria,
                    "TIPO": tipo,
                }

                # Encode payload in ISO-8859-1
                encoded_payload = {
                    key: (value.encode('iso-8859-1', errors='replace') if isinstance(value, str) else value)
                    for key, value in payload.items()
                }

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

                # Send the POST request to insert the job
                post_response = requests.post(API_URL, data=encoded_payload)
                if post_response.status_code == 200:
                    print(f"Job '{payload['TITULO']}' successfully sent.")
                else:
                    print(f"Failed to send job '{payload['TITULO']}'. HTTP Status: {post_response.status_code}")
                    print("Response Content:", post_response.text)

            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from the script tag at {job_url}.")
            except Exception as e:
                print(f"Unexpected error processing job at {job_url}: {e}")
        else:
            print(f"No JSON script tag found at {job_url}.")

    except requests.RequestException as e:
        print(f"Error fetching job URL {job_url}: {e}")

print("Processing complete.")