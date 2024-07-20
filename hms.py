from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json

import time
import googlemaps

class Hms:
    def __init__(self, driver):
        self.driver = driver


    def get_all_resturaunts(self):
        print("Getting HMS resturaunts...")
        # Make the request to the API endpoint
        self.driver.get("https://islamicservicesportal.org/api/Restaurants")

        # Get the page source, which should contain the JSON response
        page_source = self.driver.find_element(By.TAG_NAME, "pre").text

        # Parse the JSON response
        data = json.loads(page_source)

        reformatted_data = []

        for location in data:
            # Extract relevant fields
            reformatted_location = {
                "name": location["Name"],
                "address": location["Address"],
                "phone": location["Phone"],
                "state": location["State"],
                "products": location["Products"],
                "expires": location["Expires"],
                "certification": "HMS"
            }
            print(reformatted_location['name'])
            reformatted_data.append(reformatted_location)

        return reformatted_data
