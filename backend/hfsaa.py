import time
import json
import os

from bs4 import BeautifulSoup
from titlecase import titlecase
import requests


class Hfsaa:
    def __init__(self, driver):
        self.driver = driver


    def get_zone_urls(self):
        url = 'https://www.hfsaa.org/chapters'
        self.driver.get(url)
        time.sleep(10)

        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        zone_urls = []

        zone_containers = soup.find_all("a", class_="sqs-block-button-element--large sqs-button-element--secondary sqs-block-button-element")
        for zone_container in zone_containers:
            url = zone_container['href']
            zone_urls.append(url)
        return zone_urls

    def get_zone_resturaunts(self, zone_url):
        locations = []
        
        # Construct full URL if zone_url is a relative path
        if zone_url.startswith('/'):
            full_url = f"https://www.hfsaa.org{zone_url}"
        else:
            full_url = zone_url
            
        print(f"Getting resturaunts from zone: {full_url}")
        
        # Clear existing logs and enable network domain
        try:
            self.driver.execute_cdp_cmd('Network.enable', {})
            self.driver.execute_cdp_cmd('Runtime.enable', {})
        except Exception as e:
            print(f"Warning: Could not enable CDP commands: {e}")
        
        # Navigate to the page
        self.driver.get(full_url)
        
        # Wait longer for dynamic content and API calls to complete
        print("Waiting for page to fully load and API calls to complete...")
        time.sleep(20)  # Increased wait time
        

        elfsight_request = None
        
        try:
            logs = self.driver.get_log('performance')
            print(f"Retrieved {len(logs)} performance log entries")
            
            for log in logs:
                try:
                    message = json.loads(log['message'])
                    if message['message']['method'] == 'Network.requestWillBeSent':
                        request_url = message['message']['params']['request']['url']
                        # Check for Elfsight API calls
                        if 'elfsight.com' in request_url.lower():
                            elfsight_request = request_url
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error parsing log entry: {e}")
                    continue
                
        except Exception as e:
            print(f"Error retrieving performance logs: {e}")

        if elfsight_request:
            print(f"Detected Elfsight API call:")
            print(f" - {elfsight_request}")
            try:
                response = requests.get(elfsight_request)
                response.raise_for_status()
                data = response.json()
                locations.extend(self.parse_elfsight_json(data))

            except Exception as e:
                print(f"Error fetching or parsing Elfsight API response: {e}")


        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # Find the container with locations
        location_containers = soup.find_all("li", class_="list-item list-item-basic-animation")
        for location in location_containers:
            name_tag = location.find("h2", class_="list-item-content__title")
            if not name_tag:
                continue

            name = name_tag.text.strip()
            print(name)
            location_details = {
                "certification": "HFSAA",
                "name": titlecase(name)
            }
            
            # Look for website link in the name tag
            link_tag = name_tag.find("a") if name_tag else None
            if link_tag:
                location_details['website'] = link_tag['href']

            # Find the description container which contains address and phone
            description_div = location.find("div", class_="list-item-content__description")
            if description_div:
                # Extract all paragraph tags
                paragraphs = description_div.find_all("p")
                if paragraphs:
                    # First paragraph usually contains the address
                    if len(paragraphs) >= 1:
                        # Extract text from first paragraph, handling links
                        address_p = paragraphs[0]
                        address_link = address_p.find("a")
                        if address_link:
                            # Get text content, replacing <br/> with commas
                            address_text = address_link.get_text(separator=", ", strip=True)
                            location_details['address'] = address_text
                        else:
                            location_details['address'] = address_p.get_text(separator=", ", strip=True)
                    
                    # Second paragraph usually contains phone number
                    if len(paragraphs) >= 2:
                        phone_text = paragraphs[1].get_text(strip=True)
                        if phone_text:
                            location_details['phone'] = phone_text
            
            # Look for button which might contain additional info
            button_container = location.find("div", class_="list-item-content__button-container")
            if button_container:
                button = button_container.find("a", class_="list-item-content__button")
                if button and button.get('href'):
                    # If we don't have a website yet, use the button link
                    if 'website' not in location_details:
                        location_details['website'] = button['href']
                    
            locations.append(location_details)

        return locations

    def parse_elfsight_json(self, data):
            locations = []
            
            # Navigate through the JSON structure to get the locations
            widgets = data.get('data', {}).get('widgets', {})
            for widget_id, widget_data in widgets.items():
                widget_locations = widget_data.get('data', {}).get('settings', {}).get('locations', [])
                
                for location in widget_locations:
                    location_details = {
                        "certification": "HFSAA",
                        "name": titlecase(location.get('name', ''))
                    }
                    
                    # Add website if available
                    website = location.get('website', '')
                    if website:
                        location_details['website'] = website
                    
                    # Add address if available
                    address = location.get('address', '')
                    if address:
                        location_details['address'] = address
                    
                    # Add phone if available
                    phone = location.get('phone', '')
                    if phone:
                        location_details['phone'] = phone
                    
                    locations.append(location_details)
            
            print(f"Parsed {len(locations)} locations from elfsight.json")
            return locations


    def get_all_resturaunts(self):
        print("Getting HFSAA resturaunts...")
        zone_urls = self.get_zone_urls()
        print("zone urls: ", zone_urls)
        resturaunts = []

        for zone_url in zone_urls:
            resturaunts = resturaunts + self.get_zone_resturaunts(zone_url)

        return resturaunts
