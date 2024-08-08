
import googlemaps
import json

class Geocoder:
    def __init__(self, geocode_cache_filepath, API_KEY):
        self.geocode_cache_file = open(geocode_cache_filepath)
        self.geocode_cache = json.load(self.geocode_cache_file)
        self.gmaps = googlemaps.Client(key=API_KEY)

    def geocode(self, address):
            if address in self.geocode_cache:
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

    def write_cache(self):
         json.dump(self.geocode_cache, self.geocode_cache_file)
