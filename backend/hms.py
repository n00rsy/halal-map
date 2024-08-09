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

            page_source = self.driver.find_element(By.TAG_NAME, "pre").text
            data = json.loads(page_source)

            for location in data:
                reformatted_location = {
                    "name": location["Name"],
                    "address": location["Address"],
                    "phone": location["Phone"],
                    "state": location["State"],
                    "products": self.split_text_custom(location["Products"]),
                    "expires": location["Expires"],
                    "certification": "HMS"
                }
                print(reformatted_location['name'])
                locations.append(reformatted_location)

        return locations

    def split_text_custom(self, text):
        placeholder = "SPECIAL_BAKERY_ITEMS"
        modified_text = text.replace("All Bakery Items", placeholder)
        tokens = modified_text.split()
        tokens = [token.replace(placeholder, "All Bakery Items") for token in tokens]

        return tokens
