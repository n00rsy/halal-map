from selenium import webdriver
from hfsaa import Hfsaa
from hms import Hms
from geocoder import Geocoder
import json
import time
import urllib

GOOGLE_MAPS_API_KEY = 'AIzaSyBeQvkyGVlDbl91fEjxMBfgSwK7hIP4Slk'
JSON_FILENAME = 'locations.json'
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

def generate_html(resturaunts):
    # Generate HTML content
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Halal Map</title>
        <script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_API_KEY}"></script>
        <meta name="viewport" content="width=device-width">
        <script>
            function initMap() {{
                var map = new google.maps.Map(document.getElementById('map'), {{
                    zoom: 10,
                    center: {{lat: 40.4835807, lng: -74.6620381}}
                }});

                var places = {json.dumps(resturaunts)};
                var currentInfoWindow = null;

                places.forEach(function(place) {{
                    var marker = new google.maps.Marker({{
                        position: {{lat: place.lat, lng: place.lng}},
                        map: map,
                        title: place.name
                    }});

                    var infoWindow = new google.maps.InfoWindow({{
                        content: `
                            ${{place.pin}}
                        `
                    }});

                    marker.addListener('click', function() {{
                        if (currentInfoWindow) {{
                            currentInfoWindow.close();
                        }}
                        infoWindow.open(map, marker);
                        currentInfoWindow = infoWindow;
                    }});
                }});
            }}
        </script>
        <style>
            #map {{
                height: 100%;
            }}
            html, body {{
                height: 100%;
                margin: 0;
                padding: 0;
            }}
            h3 {{
            font-size: 1.5em;
            }}
            p {{
                font-size: 1em;
            }}
            button {{
                font-size: 1em;
            }}
        </style>
    </head>
    <body onload="initMap()">
        <div id="map"></div>
    </body>
    </html>
    '''

    # Save the HTML content to a file
    with open(HTML_FILENAME, 'w') as f:
        f.write(html_content)

    print("HTML file has been generated.")

def generate_pin(resturaunt):
    html = f"<div><h3>{resturaunt['name']}</h3><p><b>Certification:</b> {resturaunt['certification']}</p><p><b>Address:</b> {resturaunt['address']}</p>"
    if "phone" in resturaunt:
        html += f'<p><b>Phone:</b> <a href="tel:{resturaunt["phone"]}"> {resturaunt["phone"]}</a></p>'
    if "products" in resturaunt:
        html += f'<p><b>Products:</b> {resturaunt["products"]}</p>'
    if "expires" in resturaunt:
        html += f'<p><b>Expires:</b> {resturaunt["expires"]}</p>'

    html += f'<a href="{resturaunt["maps_url"]}" target="_blank"><button>Navigate</button></a></div>'
    return html

def generate_google_maps_url(address):
    """
    Generates a Google Maps URL for a given address.

    :param address: The address to generate the URL for
    :return: A Google Maps URL that opens in the Google Maps app on mobile devices
    """
    base_url = "https://www.google.com/maps/search/?api=1&query="
    encoded_address = urllib.parse.quote(address)
    google_maps_url = base_url + encoded_address
    return google_maps_url

def get_all_resturaunts():
    driver = setup_selenium()

    hfsaa = Hfsaa(driver)
    hms = Hms(driver)

    resturaunts = hms.get_all_resturaunts()

    driver.quit()

    geocoder = Geocoder(GOOGLE_MAPS_API_KEY)

    valid_resturaunts = []

    for resturaunt in resturaunts:
        try:
            print(f'geocoding {resturaunt["name"]}...')
            lat, lng = geocoder.geocode(resturaunt['address'])
            resturaunt['lat'] = lat
            resturaunt['lng'] = lng
            valid_resturaunts.append(resturaunt)
        except Exception as e:
            print(e)

    save_dict_to_json(valid_resturaunts, JSON_FILENAME)

def save_new_html():
    with open(JSON_FILENAME, 'r') as file:
        resturaunts = json.load(file)

    # Iterate through the array of objects
    for resturaunt in resturaunts:
        resturaunt['maps_url'] = generate_google_maps_url(resturaunt['address'])
        resturaunt['pin'] = generate_pin(resturaunt)
    generate_html(resturaunts)

if __name__ == '__main__':

    # get_all_resturaunts()
    save_new_html()

