import requests
from bs4 import BeautifulSoup
import json
import html
from data_cleaning import clean_job_data  

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

# Load the mapping.json file
mapping_file_path = "mapping.json"

try:
    with open(mapping_file_path, "r",encoding="iso-8859-1") as file:
        mappings = json.load(file)
except FileNotFoundError:
    print(f"Error: The file '{mapping_file_path}' was not found. Please ensure it exists.")
    exit(1)
except json.JSONDecodeError as e:
    print(f"Error: Failed to parse '{mapping_file_path}': {e}")
    exit(1)

# Debugging: Log loaded mappings
print("Loaded mappings:", json.dumps(mappings, indent=2))

# Specific URL for testing
test_url = "https://www.smart-recruitments.com/find-jobs-all/customer-support-with-dutch-in-lisbon-pt"

# Fetch the job details page
try:
    response = requests.get(test_url)
    if response.status_code != 200:
        print(f"Error: Failed to fetch the page. HTTP Status: {response.status_code}")
        exit(1)
    job_html_content = response.content
except requests.RequestException as e:
    print(f"Error fetching URL {test_url}: {e}")
    exit(1)

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

        # Debugging: Log the loaded JSON
        print("Parsed JSON data:", json.dumps(data, indent=2))

        # Clean the job data
        formatted_description, zona, categoria, tipo = clean_job_data(data, mappings)

        # Prepare the payload for the API request
        payload = {
            "ACCESS": api_key,
            "REF": data.get('identifier', {}).get('value', 'job001'),
            "TITULO": data.get('title', 'undisclosed'),
            "TEXTO": (
                f"{formatted_description}\n\n"
                f'<a href="{test_url}" target="_blank">Clique aqui para se candidatar!</a> '
                "ou por email para info@smart-recruitments.com"
            ),
            "ZONA": zona,
            "CATEGORIA": categoria,  # Placeholder: Update with logic for categoria_mapping
            "TIPO": tipo,  # Placeholder: Update with logic for tipo_mapping
        }

        # Debugging: Log the payload
        print("Payload to be sent:", payload)

        # Ensure that text fields are encoded in ISO-8859-1
        encoded_payload = {key: value.encode('iso-8859-1') if isinstance(value, str) else value for key, value in payload.items()}

        # Send the POST request
        response = requests.post(api_url, data=encoded_payload)

        # Check the response
        if response.status_code == 200:
            print(f"Job '{payload['TITULO']}' successfully sent.")
        else:
            print(f"Failed to send job '{payload['TITULO']}'. HTTP Status: {response.status_code}")
            print("Response Content:", response.text)

    except json.JSONDecodeError:
        print("Error: Could not decode JSON from the script tag.")
    except Exception as e:
        print(f"Unexpected error processing job: {e}")
else:
    print(f"No JSON script tag found at {test_url}")

print("Testing complete.")