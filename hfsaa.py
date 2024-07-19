places = ['boston', 'connecticut', 'dmv', 'newjersey', 'newyork', 'pennsylvania']

import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


def get_details(place):
    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.headless = True  # Run Chrome in headless mode
    driver = webdriver.Chrome(options=options)

    # URL of the website to scrape
    url = "https://www.hfsaa.org/" + place + "/"

    # Fetch the website
    driver.get(url)

    # Wait for the page to fully load
    time.sleep(5)

    # Get page source
    page_source = driver.page_source

    # Close the WebDriver
    driver.quit()
    # Parse the HTML content
    soup = BeautifulSoup(page_source, "html.parser")

    # Find the container with locations (based on the website's structure)
    locations_container = soup.find_all("div", class_="fusion-column-wrapper fusion-column-has-shadow fusion-flex-justify-content-flex-start fusion-content-layout-column")

    # List to store location details
    locations = []

        # Iterate through each location and extract details
    for location in locations_container:
        name_tag = location.find("h4", class_="fusion-title-heading")

        if not name_tag:
            continue

        name = name_tag.text.strip()

        print(name)

        link_tag = name_tag.find("a") if name_tag else None
        link = link_tag['href'] if link_tag else "N/A"

        address_tag = location.find("div", class_="fusion-text")

        address = address_tag.find("p").text.strip().replace("\n", ", ") if address_tag else "N/A"

        p = address_tag.find_all("p")
        if len(p) < 2:
            phone = "N/A"
        else:
            phone_tag = p[1] if address_tag else None
            phone = phone_tag.text.strip() if phone_tag else "N/A"

        location_details = {
            "Name": name,
            "Address": address,
            "Phone": phone,
            "Website": link
        }

        locations.append(location_details)

    return locations

locations = []

for place in places:
    locations = locations + get_details(place)

# Print the extracted locations
for loc in locations:
    print(loc)

# Optional: Save the locations to a JSON file
with open('locations.json', 'w') as f:
    json.dump(locations, f, indent=4)
