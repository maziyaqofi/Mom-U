import requests
import os

# NHS Website Content API v2 - Sandbox
API_URL = (
    "https://sandbox.api.service.nhs.uk"
    "/nhs-website-content/pregnancy"
)

# Public sandbox test key from NHS API documentation
SANDBOX_API_KEY = os.getenv("NHS_SANDBOX_API_KEY", "").strip()

headers = {
    "Accept": "application/json",
    "apikey": SANDBOX_API_KEY,
}

print("NHS Pregnancy Sandbox Test")
print("API URL:", API_URL)

try:
    response = requests.get(
        API_URL,
        headers=headers,
        timeout=20,
    )

    print("HTTP Status:", response.status_code)
    print(
        "Content Type:",
        response.headers.get("Content-Type"),
    )

    if response.status_code == 200:
        data = response.json()

        print("API request succeeded.")
        print("Response type:", data.get("@type"))
        print("Page name:", data.get("name"))
        print("Description:", data.get("description"))
        print("Available fields:", list(data.keys()))

    else:
        print("API request did not succeed.")
        print("Response preview:", response.text[:300])

except requests.RequestException as error:
    print("Request failed:", error)