import requests

# This header makes your script look like it's a real Chrome browser on Windows.
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    # Send the request with the new header
    response = requests.get("https://fbref.com", headers=headers, timeout=10)
    
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        print("Success! Connection is live and access is granted.")
    elif response.status_code == 403:
        print("Still blocked. The site may have more advanced bot detection.")
    else:
        print(f"Connection is live, but received a different status: {response.status_code}")

except Exception as e:
    print(f"Connection failed: {e}")