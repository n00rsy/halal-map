from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json

import time
import googlemaps

# Path to your WebDriver executable
# webdriver_path = '/path/to/chromedriver'

# Set up headless browser options
options = Options()
options.headless = True
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")

# Initialize the WebDriver
# service = Service(webdriver_path)
driver = webdriver.Chrome(options=options)

# Make the request to the API endpoint
driver.get("https://islamicservicesportal.org/api/Restaurants")

# Get the page source, which should contain the JSON response
page_source = driver.find_element(By.TAG_NAME, "pre").text

# Parse the JSON response
data = json.loads(page_source)

# Close the WebDriver
driver.quit()

# Print the JSON response
print(json.dumps(data, indent=4))

# Store the result in a dictionary
result_dict = data

places_list = []

# Google Maps API Key
API_KEY = 'AIzaSyBeQvkyGVlDbl91fEjxMBfgSwK7hIP4Slk'

gmaps = googlemaps.Client(key=API_KEY)

# Iterate through the JSON list
for entry in result_dict:
    name = entry["Name"]
    address = entry["Address"]

    # Geocoding the address
    geocode_result = gmaps.geocode(address)

    if geocode_result:
        # Extracting the location details
        location = geocode_result[0]['geometry']['location']
        lat = location['lat']
        lng = location['lng']

        place_details = {
            "Name": name,
            "Address": address,
            "Latitude": lat,
            "Longitude": lng,
            "Phone": entry["Phone"],
            "Products": entry["Products"],
            "Expires": entry["Expires"]
        }

        places_list.append(place_details)

        # Print the place details
        print(f"Name: {name}")
        print(f"Address: {address}")
        print(f"Latitude: {lat}")
        print(f"Longitude: {lng}")
        print(f"Phone: {entry['Phone']}")
        print(f"Products: {entry['Products']}")
        print(f"Expires: {entry['Expires']}")
        print("\n")

        # Sleep to avoid hitting the API rate limit
        time.sleep(1)
    else:
        print(f"Geocoding failed for address: {address}")


import json

# Sample JSON data
json_data = places_list

# Generate HTML content
html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Places Map</title>
    <script src="https://maps.googleapis.com/maps/api/js?key={API_KEY}"></script>
    <script>
        function initMap() {{
            var map = new google.maps.Map(document.getElementById('map'), {{
                zoom: 10,
                center: {{lat: 41.7153, lng: -88.2126}}
            }});

            var places = {json.dumps(json_data)};

            places.forEach(function(place) {{
                var marker = new google.maps.Marker({{
                    position: {{lat: place.Latitude, lng: place.Longitude}},
                    map: map,
                    title: place.Name
                }});

                var infoWindow = new google.maps.InfoWindow({{
                    content: `
                        <div>
                            <h3>${{place.Name}}</h3>
                            <p><b>Address:</b> ${{place.Address}}</p>
                            <p><b>Phone:</b> ${{place.Phone}}</p>
                            <p><b>Products:</b> ${{place.Products}}</p>
                            <p><b>Expires:</b> ${{place.Expires}}</p>
                        </div>
                    `
                }});

                marker.addListener('click', function() {{
                    infoWindow.open(map, marker);
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
    </style>
</head>
<body onload="initMap()">
    <div id="map"></div>
</body>
</html>
'''

# Save the HTML content to a file
with open('index.html', 'w') as f:
    f.write(html_content)

print("HTML file has been generated.")
