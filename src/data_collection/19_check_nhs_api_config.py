import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read NHS API key
api_key = os.getenv("NHS_API_KEY", "").strip()

print("NHS API Configuration Check")

if api_key:
    print("API key configured: Yes")
    print("Ready for authenticated API testing.")
else:
    print("API key configured: No")
    print("Check the NHS API documentation and access requirements.")
    