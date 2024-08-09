from selenium import webdriver
from hfsaa import Hfsaa
from hms import Hms
from gmaps_driver import GmapsDriver
import json

GOOGLE_MAPS_API_KEY = ''
JSON_FILENAME = '../locations.json'
GMAPS_CACHE_FILEPATH = 'gmaps_cache.json'
HTML_FILENAME = 'index.html'

def setup_selenium():
    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.headless = True  # Run Chrome in headless mode
    return webdriver.Chrome(options=options)

def save_dict_to_json(data, filename):
    """
    Saves a dictionary to a JSON file.

    :param data: Dictionary to save
    :param filename: Name of the JSON file
    """
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)

def get_all_resturaunts():
    driver = setup_selenium()

    hfsaa = Hfsaa(driver)
    hms = Hms(driver)

    resturaunts = hms.get_all_resturaunts()
    resturaunts = resturaunts + hfsaa.get_all_resturaunts()
    driver.quit()

    gmaps_driver = GmapsDriver(GMAPS_CACHE_FILEPATH, GOOGLE_MAPS_API_KEY)

    valid_resturaunts = []
    for resturaunt in resturaunts:
        try:
            print(f'processing {resturaunt["name"]}...')
            placeid, lat, lng = gmaps_driver.geocode(resturaunt['address'])
            resturaunt['lat'] = lat
            resturaunt['lng'] = lng
            resturaunt['nav_url'] = gmaps_driver.generate_google_maps_url(resturaunt['address'], placeid)

            valid_resturaunts.append(resturaunt)
        except Exception as e:
            print(e)
    # save cache for next time
    gmaps_driver.write_cache()

    save_dict_to_json(valid_resturaunts, JSON_FILENAME)

if __name__ == '__main__':
    get_all_resturaunts()
