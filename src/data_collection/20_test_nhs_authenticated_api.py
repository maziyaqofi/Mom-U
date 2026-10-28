import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("NHS_API_KEY", "").strip()

if not api_key:
    raise RuntimeError("NHS_API_KEY is not configured.")

# NHS Integration Test endpoint
# Confirm this URL against the API v2 documentation.
base_url = "https://int.api.service.nhs.uk/nhs-website-content"

# Official NHS integration test example endpoint
article_path = "/conditions/"

api_url = base_url + article_path

headers = {
    "Accept": "application/json",
    "apikey": api_key,
    "User-Agent": "Mom-U-Research/1.0"
}

print("NHS Authenticated API Test")
print("Environment: Integration Test")
print("API URL:", api_url)

try:
    response = requests.get(
        api_url,
        headers=headers,
        timeout=20
    )

    print("HTTP Status:", response.status_code)

    print("Response URL:", response.url)
    print("Server:", response.headers.get("Server", "Not provided"))
    print("Request ID:", response.headers.get("X-Request-ID", "Not provided"))
    from html.parser import HTMLParser

    class HTMLTextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.parts = []

        def handle_data(self, data):
            text = data.strip()
            if text:
                self.parts.append(text)


    parser = HTMLTextExtractor()
    parser.feed(response.text)

    print("Response Message:", " ".join(parser.parts)[:1500])

    print(
        "Content Type:",
        response.headers.get("Content-Type")
    )

    if response.status_code == 200:
        print("Authenticated API request succeeded.")

        try:
            data = response.json()

            if isinstance(data, dict):
                print("Response fields:", list(data.keys()))
            else:
                print("Response type:", type(data).__name__)

        except ValueError:
            print("Response is not valid JSON.")

    elif response.status_code == 401:
        print("Authentication failed.")

    elif response.status_code == 403:
        print("Access forbidden.")

    elif response.status_code == 404:
        print("Endpoint or article not found.")

    else:
        print("Unexpected API response.")

except requests.RequestException as error:
    print("Request failed:", error)