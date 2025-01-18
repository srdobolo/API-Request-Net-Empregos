import requests
from bs4 import BeautifulSoup
import json
import html
from data_cleaning import clean_job_data  # Assuming you have this function implemented

# Base URL for the find-jobs section
base_url = 'https://smart-recruitments.com/find-jobs-all/'

# API endpoint and key
api_url = "http://partner.net-empregos.com/hrsmart_insert.asp"
remove_api_url = "http://partner.net-empregos.com/hrsmart_remove.asp"
key_file_path = "API_ACCESS_KEY"
mapping_file_path = "mapping.json"

# Read the API key
try:
    with open(key_file_path, "r") as file:
        api_key = file.read().strip()
except FileNotFoundError:
    print(f"Error: The file '{key_file_path}' was not found. Please ensure it exists.")
    exit(1)

# Load the mapping file
try:
    with open(mapping_file_path, "r", encoding="iso-8859-1") as file:
        mappings = json.load(file)
except FileNotFoundError:
    print(f"Error: The file '{mapping_file_path}' was not found. Please ensure it exists.")
    exit(1)
except json.JSONDecodeError as e:
    print(f"Error: Failed to parse '{mapping_file_path}': {e}")
    exit(1)

# Step 1: Load the main jobs page to find all job links
try:
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Error: Failed to fetch the base URL. HTTP Status: {response.status_code}")
        exit(1)
    html_content = response.content
except requests.RequestException as e:
    print(f"Error fetching base URL: {e}")
    exit(1)

# Step 2: Parse the HTML with BeautifulSoup to find all job links
soup = BeautifulSoup(html_content, 'html.parser')

# Extract job links, deduplicate, and filter those ending with "pt"
job_links = list(set([
    a['href'] for a in soup.find_all('a', href=True)
    if '/find-jobs-all/' in a['href'] and a['href'].endswith('pt')
]))

print(f"Found {len(job_links)} job(s) to process ending with 'pt'.")

# Step 3: Process each job link
for job_url in job_links:
    try:
        # Fetch the job details page
        response = requests.get(job_url)
        if response.status_code != 200:
            print(f"Error: Failed to fetch the page {job_url}. HTTP Status: {response.status_code}")
            continue
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
                    "ACCESS": api_key,
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
                encoded_payload = {key: value.encode('iso-8859-1') if isinstance(value, str) else value for key, value in payload.items()}

                # Prepare and send the removal request
                remove_payload = {
                    "ACCESS": api_key,
                    "REF": data.get('identifier', {}).get('value', 'job001'),
                }

                try:
                    remove_response = requests.get(remove_api_url, params=remove_payload)
                    if remove_response.status_code == 200:
                        print(f"Job '{remove_payload['REF']}' successfully removed.")
                    else:
                        print(f"Failed to remove job '{remove_payload['REF']}'. HTTP Status: {remove_response.status_code}")
                        print("Response Content:", remove_response.text)
                except requests.RequestException as e:
                    print(f"Error removing job '{remove_payload['REF']}': {e}")
                    continue

                # Send the POST request to insert the job
                post_response = requests.post(api_url, data=encoded_payload)
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