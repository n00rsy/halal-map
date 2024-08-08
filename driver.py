from selenium import webdriver
from hfsaa import Hfsaa
from hms import Hms
from geocoder import Geocoder
import json

GOOGLE_MAPS_API_KEY = ''
JSON_FILENAME = 'locations.json'
GEOCODE_CACHE_FILENAME = 'geocode_cache.json'
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

    geocoder = Geocoder(GEOCODE_CACHE_FILENAME, GOOGLE_MAPS_API_KEY)

    valid_resturaunts = []
    for resturaunt in resturaunts:
        try:
            print(f'geocoding {resturaunt["name"]}...')
            lat, lng = geocoder.geocode(resturaunt['address'])
            resturaunt['lat'] = lat
            resturaunt['lng'] = lng
            resturaunt['nav_url'] = geocoder.generate_google_maps_url(resturaunt['address'])
            valid_resturaunts.append(resturaunt)
        except Exception as e:
            print(e)
    # save cache for next time
    geocoder.write_cache()

    save_dict_to_json(valid_resturaunts, JSON_FILENAME)

if __name__ == '__main__':

    get_all_resturaunts()

