import urllib.request
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["crawlerdb"]
pages_collection = db["pages"]

# Define the Frontier class to manage URLs to visit and visited URLs
class Frontier:
    def __init__(self):
        self.to_visit = []  # List of URLs to be visited
        self.visited = set()  # Set of already visited URLs
        self.done_flag = False  # Flag to indicate completion

    # Add a URL to the frontier if it hasn't been visited or already added
    def addURL(self, url):
        if url not in self.visited and url not in self.to_visit:
            self.to_visit.append(url)

    # Retrieve the next URL to visit and mark it as visited
    def nextURL(self):
        if self.to_visit:
            url = self.to_visit.pop(0)  # Get the first URL in the queue
            self.visited.add(url)  # Mark URL as visited
            return url
        else:
            return None

    # Check if crawling is complete (no URLs left to visit or done flag set)
    def done(self):
        return self.done_flag or not self.to_visit

    # Clear all URLs in the frontier and mark crawling as complete
    def clear_frontier(self):
        self.to_visit = []
        self.done_flag = True

# Retrieve HTML content from a given URL, ensuring it is an HTML resource
def retrieveHTML(url):
    try:
        response = urllib.request.urlopen(url)
        content_type = response.headers.get('Content-Type')
        if 'text/html' in content_type:
            html = response.read()
            return html
        else:
            return None
    except Exception as e:
        print(f"Failed to retrieve {url}: {e}")
        return None

# Store the HTML content of a page in the MongoDB database
def storePage(url, html):
    pages_collection.insert_one({'url': url, 'html': html.decode('utf-8')})

# Parse the HTML content to extract valid links within the CS website
def parse(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    urls = []
    for link in soup.find_all('a', href=True):  # Find all anchor tags with href attribute
        href = link['href']
        # Build absolute URL from the base URL and relative href
        href = urljoin(base_url, href)
        # Only consider HTTP and HTTPS URLs
        parsed_href = urlparse(href)
        if parsed_href.scheme in ['http', 'https']:
            # Only considering HTML and SHTML pages
            path = parsed_href.path
            if path.endswith('.html') or path.endswith('.shtml') or path.endswith('.htm') or path == '' or path.endswith('/'):
                # Only considering URLs within the CS website domain
                if href.startswith('https://www.cpp.edu/sci/computer-science/'):
                    urls.append(href)
    return urls

# Check if the page is the target by finding the specific h1 tag for "Permanent Faculty"
def targetpage(html):
    soup = BeautifulSoup(html, 'html.parser')
    h1 = soup.find('h1', class_='cpp-h1')
    if h1 and h1.text.strip() == 'Permanent Faculty':
        return True
    return False

# Print message indicating that the target page has been found
def flagTargetPage(url):
    print(f"Target page found: {url}")

# Main crawling function that iterates through URLs in the frontier until the target is found
def crawlerThread(frontier):
    while not frontier.done():
        url = frontier.nextURL()
        if url is None:
            break
        print(f"Visiting: {url}")
        html = retrieveHTML(url)
        if html:
            storePage(url, html)  # Store the HTML in MongoDB
            if targetpage(html):  # Check if it’s the target page
                flagTargetPage(url)  # Flag the target page if found
                frontier.clear_frontier()  # Stop further crawling
            else:
                urls = parse(html, url)  # Parse HTML for additional links
                for link in urls:
                    if link not in frontier.visited:
                        frontier.addURL(link)  # Add each new URL to the frontier

# Initialize and start the crawling process
if __name__ == "__main__":
    start_url = 'https://www.cpp.edu/sci/computer-science/'
    frontier = Frontier()  # Create a new frontier for URLs
    frontier.addURL(start_url)  # Add the start URL to the frontier
    crawlerThread(frontier)  # Start the crawler thread
