import time
from bs4 import BeautifulSoup

class Hfsaa:
    def __init__(self, driver):
        self.driver = driver


    def get_zone_urls(self):
        # URL of the website to scrape
        url = 'https://www.hfsaa.org/restaurants/'

        # Fetch the website
        self.driver.get(url)

        # Wait for the page to fully load
        time.sleep(5)

        # Get page source
        page_source = self.driver.page_source

        # Parse the HTML content
        soup = BeautifulSoup(page_source, "html.parser")

        zone_urls = []

        # Find the container with locations (based on the website's structure)
        zone_containers = soup.find_all("a", class_="fusion-column-anchor")
        for zone_container in zone_containers:
            url = zone_container['href']
            zone_urls.append(url)
        return zone_urls


    def get_zone_resturaunts(self, zone_url):
        print(f"Getting resturaunts from zone: {zone_url}")
        # Fetch the website
        self.driver.get(zone_url)

        # Wait for the page to fully load
        time.sleep(5)

        # Get page source
        page_source = self.driver.page_source

        # Parse the HTML content
        soup = BeautifulSoup(page_source, "html.parser")

        # Find the container with locations (based on the website's structure)
        location_containers = soup.find_all("div", class_="fusion-column-wrapper fusion-column-has-shadow fusion-flex-justify-content-flex-start fusion-content-layout-column")

        # List to store location details
        locations = []

            # Iterate through each location and extract details
        for location in location_containers:
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
                "name": name,
                "address": address,
                "phone": phone,
                "website": link,
                "certification": "HFSAA"
            }

            locations.append(location_details)

        return locations


    def get_all_resturaunts(self):
        print("Getting HFSAA resturaunts...")
        zone_urls = self.get_zone_urls()
        resturaunts = []

        for zone_url in zone_urls:
            resturaunts = resturaunts + self.get_zone_resturaunts(zone_url)

        return resturaunts
