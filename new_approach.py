import requests

# URL of the endpoint
url = "http://partner.net-empregos.com/hrsmart_insert.asp"

# Data to be sent (same as the cURL form data)
data = {
    "ACCESS": "6F89DD1C1E8D4CD2",
    "REF": "job001",
    "TITULO": "Software Engineer",
    "TEXTO": "We are looking for a skilled software engineer...",
    "ZONA": "1",
    "CATEGORIA": "10",
    "TIPO": "1"
}

# Send POST request with form data
response = requests.post(url, data=data)

# Print the response from the server
print(response.status_code)
print(response.text)