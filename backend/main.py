import json
import os
from datetime import datetime

from gmaps_driver import GmapsDriver
from hfsaa import Hfsaa
from hms import Hms
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

GMAPS_API_KEY = os.getenv('GMAPS_API_KEY')
LOCATIONS_FILEPATH = os.getenv('LOCATIONS_FILEPATH')
GMAPS_CACHE_FILEPATH = os.getenv('GMAPS_CACHE_FILEPATH')


def setup_selenium():
    chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    chrome_options = Options()
    options = [
    "--headless",
    "--window-size=1920,1200",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--no-sandbox",
    "--disable-dev-shm-usage"
    "--disable-web-security",
    "--allow-running-insecure-content"
    ]
    for option in options:
        chrome_options.add_argument(option)
    
    # Enable performance logging to capture network requests
    chrome_options.set_capability('goog:loggingPrefs', {
        'performance': 'ALL',
        'browser': 'ALL'
    })
    
    # Enable CDP (Chrome DevTools Protocol) for network monitoring
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    return webdriver.Chrome(service=chrome_service, options=chrome_options)


def export_locations(locations, filename):
    timestamp = datetime.now()
    current_date = timestamp.strftime("%b %d, %Y")
    data = {
        "timestamp": int(timestamp.timestamp()),
        "updated": current_date,
        "places": locations
    }
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)


def get_all_resturaunts():
    driver = setup_selenium()

    hfsaa = Hfsaa(driver)
    hms = Hms(driver)

    hms_resturaunts = hms.get_all_resturaunts()
    hfsaa_resturaunts = hfsaa.get_all_resturaunts()
    driver.quit()
    return hms_resturaunts + hfsaa_resturaunts


def process_resturaunts(resturaunts):
    gmaps_driver = GmapsDriver(GMAPS_CACHE_FILEPATH, GMAPS_API_KEY)
    valid_resturaunts = []
    for resturaunt in resturaunts:
        try:
            print(f'processing {resturaunt["name"]}...')
            placeid, lat, lng = gmaps_driver.geocode(resturaunt['name'], resturaunt['address'])
            resturaunt['lat'] = lat
            resturaunt['lng'] = lng
            resturaunt['nav_url'] = gmaps_driver.generate_google_maps_url(resturaunt['address'], placeid)

            valid_resturaunts.append(resturaunt)
        except Exception as e:
            print(e)
    # save cache for next time
    gmaps_driver.write_cache()
    return valid_resturaunts


if __name__ == '__main__':
    resturaunts = get_all_resturaunts()
    print(json.dumps(resturaunts))
    valid_resturaunts = process_resturaunts(resturaunts)
    export_locations(valid_resturaunts, LOCATIONS_FILEPATH)
