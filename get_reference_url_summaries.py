import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# List of URLs to process
urls = []
with open("reference_projects.txt") as f:
    for line in f:
        url = line.strip()
        if not url: continue
        if not url.startswith("http"): continue
        urls.append(url)

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_page_title(url):
    """Fetches a URL and extracts the title using BeautifulSoup."""
    try:
        # Send a GET request with a timeout
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Parse the HTML content
        soup = BeautifulSoup(response.text, features='lxml')

        # Find the title tag
        title_tag = soup.find('title')
        if title_tag:
            # Get the text and clean it up (strip whitespace)
            title = title_tag.get_text().strip()
            # Replace newlines and excessive spaces for cleaner output
            title = ' '.join(title.split())
            return title
        else:
            return "No title tag found"

    except requests.exceptions.Timeout:
        return "Error: Request timed out"
    except requests.exceptions.HTTPError as e:
        return f"Error: HTTP {e.response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error: An unexpected error occurred - {e}"

# Main execution
print("Starting page summary...")
print("-" * 50)

for i, url in enumerate(urls):
    print(f"\nURL {i+1}: {url}")
    print(f"Domain: {urlparse(url).netloc}")

    title = get_page_title(url)
    print(f"Title: {title}")

print("\n" + "-" * 50)
print("Page summary complete.")