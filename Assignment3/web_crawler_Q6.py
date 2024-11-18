import pymongo
import urllib.request
from bs4 import BeautifulSoup

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["crawlerdb"]
pages_collection = db["pages"]
professors_collection = db["professors"]

# Ensure a unique index on 'email' field to prevent duplicate entries
professors_collection.create_index('email', unique=True)
print("Ensured unique index on 'email'.")

# Target URL for the Permanent Faculty page
target_url = 'https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml'

# Always download the page to get the latest content
print("Downloading the Permanent Faculty page...")
try:
    response = urllib.request.urlopen(target_url)
    html_data = response.read().decode('utf-8')  # Read and decode the page content
except Exception as e:
    print(f"Failed to retrieve the page: {e}")
    exit(1)

# Parse the HTML data with BeautifulSoup
soup = BeautifulSoup(html_data, 'html.parser')

# Find the section containing the faculty member information
faculty_section = soup.find('section', class_='text-images')

# Check if the faculty section is found
if not faculty_section:
    print("Faculty section not found. Please check the HTML structure.")
    exit(1)

# Locate all <h2> tags within the faculty section, as they indicate individual faculty members
h2_tags = faculty_section.find_all('h2')

print(f"Found {len(h2_tags)} faculty profiles.")

# If no faculty profiles are found, display an error and exit
if not h2_tags:
    print("No faculty profiles found. Please check the HTML structure.")
    exit(1)

# Function to extract label-value pairs from <strong> tags
def get_label_value(strong_tag):
    # Get the label text, strip extra characters, and convert to lowercase for consistency
    label = strong_tag.get_text(strip=True).lower().rstrip(':')
    
    # Start collecting text from the sibling after the <strong> tag
    current = strong_tag.next_sibling

    # Skip over whitespace, colons, or line breaks
    while current and (isinstance(current, str) and current.strip() in ['', ':'] or current.name == 'br'):
        current = current.next_sibling

    # Collect all text until the next <strong> tag or end of the section
    value_parts = []
    while current and not (hasattr(current, 'name') and current.name == 'strong'):
        if isinstance(current, str):
            text = current.strip()
            if text and text != ':':
                value_parts.append(text)
        elif current.name == 'a':  # Handle <a> tags for email and web fields
            if label == 'email':
                value_parts.append(current.get_text(strip=True))
            elif label == 'web':
                value_parts.append(current.get('href', '').strip())
            else:
                value_parts.append(current.get_text(strip=True))
        elif current.name == 'br':
            pass  # Skip line breaks
        else:
            value_parts.append(current.get_text(strip=True))
        current = current.next_sibling
    value = ' '.join(value_parts).strip()  # Combine all parts into a single string
    return label, value

# Set to keep track of processed emails to avoid duplicates
processed_emails = set()

# Loop through each <h2> tag, representing a faculty member
for name_tag in h2_tags:
    name = name_tag.get_text(strip=True)  # Extract the name from the <h2> tag

    # Initialize variables for each attribute to None
    title = office = phone = email = website = None

    # Find the <p> tag following the <h2> tag, which contains the faculty details
    p_tag = name_tag.find_next_sibling('p')

    if p_tag:
        # Extract and process each <strong> tag in the <p> tag
        strong_tags = p_tag.find_all('strong')
        for strong_tag in strong_tags:
            label, value = get_label_value(strong_tag)
            # Assign the value to the appropriate variable based on the label
            if label == 'title':
                title = value
            elif label == 'office':
                office = value
            elif label == 'phone':
                phone = value
            elif label == 'email':
                email = value
            elif label == 'web':
                website = value

    # Ensure both name and email are present, as they are critical information
    if not name or not email:
        print(f"Missing critical information for a faculty member ({name}). Skipping.")
        continue

    # Check for duplicate email in the current run to avoid re-processing
    if email in processed_emails:
        print(f"Duplicate email found in HTML for {name} ({email}). Skipping duplicate.")
        continue
    processed_emails.add(email)

    # Create a dictionary with all faculty member data
    professor_data = {
        'name': name,
        'title': title,
        'office': office,
        'phone': phone,
        'email': email,
        'website': website
    }

    # Insert data into MongoDB and handle any duplicate errors
    try:
        professors_collection.insert_one(professor_data)
        print(f"Inserted professor: {name}")
        # Optional: Print the extracted data for verification
        print(f"Name: {name}")
        print(f"Title: {title}")
        print(f"Office: {office}")
        print(f"Phone: {phone}")
        print(f"Email: {email}")
        print(f"Website: {website}")
        print("---")
    except pymongo.errors.DuplicateKeyError:
        print(f"Professor with email {email} already exists in MongoDB. Skipping.")

# Printing the total number of unique professors inserted
print(f"Total professors inserted: {len(processed_emails)}")
