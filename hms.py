from selenium.webdriver.common.by import By
import json


class Hms:
    def __init__(self, driver):
        self.driver = driver


    def get_all_resturaunts(self):
        urls = ['https://islamicservicesportal.org/api/Retailers', "https://islamicservicesportal.org/api/Restaurants"]
        locations = []

        for url in urls:
            print(f"Getting HMS... {url}")
            self.driver.get(url)

            # Get the page source, which should contain the JSON response
            page_source = self.driver.find_element(By.TAG_NAME, "pre").text
            data = json.loads(page_source)

            for location in data:
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
                locations.append(reformatted_location)

        return locations
