import requests
from bs4 import BeautifulSoup
import json
import html
from urllib.parse import urlencode

# Base URL for the find-jobs section
base_url = 'https://smart-recruitments.com/find-jobs-all/'

# API endpoint and key
api_url = "http://partner.net-empregos.com/hrsmart_insert.asp"

# Read the API key from a file
key_file_path = "API_ACCESS_KEY"
with open(key_file_path, "r") as file:
    api_key = file.read().strip()  # Strip to remove any surrounding whitespace or newlines

# Step 1: Load the main jobs page to find all job links
response = requests.get(base_url)
html_content = response.content

# Step 2: Parse the HTML with BeautifulSoup to find all job links
soup = BeautifulSoup(html_content, 'html.parser')

# Extract job links, deduplicate, and filter those ending with "pt"
job_links = list(set([
    a['href'] for a in soup.find_all('a', href=True)
    if '/find-jobs-all/' in a['href'] and a['href'].endswith('pt')
]))

# Log the number of job links found
print(f"Found {len(job_links)} job(s) to process ending with 'pt'.")

# Step 3: Iterate over each job link, fetch its content, and extract the JSON
for job_link in job_links:
    # Full URL for each job link
    job_url = base_url + job_link.split('/')[-1]

    # Fetch the job details page
    response = requests.get(job_url)
    job_html_content = response.content

    # Parse the HTML with BeautifulSoup
    job_soup = BeautifulSoup(job_html_content, 'html.parser')

    # Locate the <script> tag containing the JSON
    script_tag = job_soup.find('script', type='application/ld+json')

    if script_tag and script_tag.string:
        json_content = script_tag.string

        try:
            # Unescape any HTML entities that may be in the JSON content
            json_content_unescaped = html.unescape(json_content)

            # Parse the JSON content
            data = json.loads(json_content_unescaped)

            # Prepare the payload for the API request
            payload = {
                "ACCESS": api_key,
                "REF": data.get('identifier', {}).get('value', 'job001'),  # Default to 'job001' if missing
                "TITULO": data.get('title', 'undisclosed'),
                "TEXTO": data.get('description', 'No description provided.'),
                "ZONA": "1",  # Adjust as needed
                "CATEGORIA": "10",  # Adjust as needed
                "TIPO": "1",  # Adjust as needed
            }

            # Log the payload
            print(f"Sending payload: {payload}")

            # Send the POST request
            response = requests.post(api_url, data=payload)

            # Check the response
            if response.status_code == 200:
                print(f"Job '{payload['TITULO']}' successfully sent.")
            else:
                print(f"Failed to send job '{payload['TITULO']}'. HTTP Status: {response.status_code}, Response: {response.text}")

        except json.JSONDecodeError:
            print(f"Error decoding JSON from {job_url}")
        except Exception as e:
            print(f"Error processing job '{job_url}': {e}")

print("All jobs processed.")