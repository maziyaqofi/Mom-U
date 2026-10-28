import requests

# NHS Website Content API base URL
base_url = "https://api.nhs.uk"

# Example pregnancy article path
article_path = "/pregnancy/your-pregnancy-care/12-week-scan/"

# Build API URL
api_url = base_url + article_path

# Send a test request without credentials
try:
    response = requests.get(
        api_url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Mom-U-Research/1.0"
        },
        timeout=15
    )

    print("NHS API Feasibility Check")
    print("Request URL:", api_url)
    print("HTTP Status:", response.status_code)
    print("Content Type:", response.headers.get("Content-Type"))

    if response.status_code == 200:
        print("API endpoint is accessible.")

        try:
            data = response.json()
            print("Response fields:", list(data.keys()))
        except ValueError:
            print("Response is not valid JSON.")

    elif response.status_code in (401, 403):
        print("Access denied or authentication required.")

    elif response.status_code == 404:
        print("Endpoint or article path not found.")

    else:
        print("API returned an unexpected status.")

except requests.RequestException as error:
    print("Request failed:", error)