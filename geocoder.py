
import googlemaps
import json
import urllib

class Geocoder:
    def __init__(self, geocode_cache_filepath, API_KEY):
        self.geocode_cache_filepath = geocode_cache_filepath
        geocode_cache_file = open(geocode_cache_filepath, 'r')
        self.geocode_cache = json.load(geocode_cache_file)
        geocode_cache_file.close()
        self.gmaps = googlemaps.Client(key=API_KEY)


    def geocode(self, address):
            if address in self.geocode_cache:
                print("cache hit: ", address)
                return self.geocode_cache[address]

            geocode_result = self.gmaps.geocode(address)
            if geocode_result:
                # Extracting the location details
                location = geocode_result[0]['geometry']['location']
                lat = location['lat']
                lng = location['lng']
                self.geocode_cache[address] = (lat, lng)
                return (lat, lng)
            else:
                raise Exception(f"invalid address:{address}")

    def generate_google_maps_url(self, address):
        """
        Generates a Google Maps URL for a given address.

        :param address: The address to generate the URL for
        :return: A Google Maps URL that opens in the Google Maps app on mobile devices
        """
        base_url = "https://www.google.com/maps/search/?api=1&query="
        encoded_address = urllib.parse.quote(address)
        google_maps_url = base_url + encoded_address
        return google_maps_url

    def write_cache(self):
        with open(self.geocode_cache_filepath, 'w') as file:
            json.dump(self.geocode_cache, file)
