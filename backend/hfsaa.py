import time

from bs4 import BeautifulSoup
from titlecase import titlecase


class Hfsaa:
    def __init__(self, driver):
        self.driver = driver


    def get_zone_urls(self):
        url = 'https://www.hfsaa.org/restaurants/'
        self.driver.get(url)
        time.sleep(5)

        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        zone_urls = []

        # Find the container with zones
        zone_containers = soup.find_all("a", class_="fusion-column-anchor")
        for zone_container in zone_containers:
            url = zone_container['href']
            zone_urls.append(url)

        zone_containers = soup.find_all("a", class_="icon-accountant-map")
        for zone_container in zone_containers:
            url = zone_container['href']
            zone_urls.append(url)
        return zone_urls


    def get_zone_resturaunts(self, zone_url):
        print(f"Getting resturaunts from zone: {zone_url}")
        self.driver.get(zone_url)
        time.sleep(5)

        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Find the container with locations
        location_containers = soup.find_all("div", class_="fusion-column-wrapper fusion-column-has-shadow fusion-flex-justify-content-flex-start fusion-content-layout-column")
        locations = []
        for location in location_containers:
            name_tag = location.find("h4", class_="fusion-title-heading")
            if not name_tag:
                continue

            name = name_tag.text.strip()
            print(name)
            location_details = {
                "certification": "HFSAA",
                "name": titlecase(name)
            }
            link_tag = name_tag.find("a") if name_tag else None
            if link_tag:
                location_details['website'] = link_tag['href']

            address_tag = location.find("div", class_="fusion-text")
            if address_tag:
                location_details['address'] = address_tag.find("p").text.strip().replace("\n", ", ")

            p = address_tag.find_all("p")
            if len(p) >= 2 and p[1]:
                    location_details['phone'] = p[1].text.strip()
            locations.append(location_details)

        return locations


    def get_all_resturaunts(self):
        print("Getting HFSAA resturaunts...")
        zone_urls = self.get_zone_urls()
        print("zone urls: ", zone_urls)
        resturaunts = []

        for zone_url in zone_urls:
            resturaunts = resturaunts + self.get_zone_resturaunts(zone_url)

        return resturaunts
