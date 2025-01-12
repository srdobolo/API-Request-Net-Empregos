import requests
from bs4 import BeautifulSoup
import json
import html
from urllib.parse import urlencode

# API endpoint and key
api_url = "http://partner.net-empregos.com/hrsmart_insert.asp"

# Read the API key from a file
key_file_path = "API_ACCESS_KEY"

try:
    with open(key_file_path, "r") as file:
        api_key = file.read().strip()  # Strip to remove any surrounding whitespace or newlines
except FileNotFoundError:
    print(f"Error: The file '{key_file_path}' was not found. Please ensure it exists.")
    exit(1)

# Specific URL for testing
test_url = "https://www.smart-recruitments.com/find-jobs-all/customer-support-with-dutch-in-lisbon-pt"

# Fetch the job details page
response = requests.get(test_url)
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
            "REF": data.get('identifier', {}).get('value', 'job001'),
            "TITULO": data.get('title', 'undisclosed'),
            "TEXTO": data.get('description', 'No description provided.'),
            "ZONA": "Lisboa",  
            "CATEGORIA": "Call Center / Help Desk",  
            "TIPO": data.get('employmentType', 'undisclosed'),  
        }

        # Log the payload
        print(f"Payload to be sent: {payload}")

        # Send the POST request
        response = requests.post(api_url, data=payload)

        # Check the response
        if response.status_code == 200:
            print(f"Job '{payload['TITULO']}' successfully sent.")
        else:
            print(f"Failed to send job '{payload['TITULO']}'. HTTP Status: {response.status_code}, Response: {response.text}")
            print(f"Payload Sent: {payload}")

    except json.JSONDecodeError:
        print(f"Error decoding JSON from {test_url}")
    except Exception as e:
        print(f"Error processing job '{test_url}': {e}")
else:
    print(f"No JSON script tag found in {test_url}")

print("Testing complete.")