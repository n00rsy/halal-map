
import googlemaps
import json
import urllib

class GmapsDriver:
    def __init__(self, gmaps_cache_filepath, API_KEY):
        self.gmaps_cache_filepath = gmaps_cache_filepath
        with open(gmaps_cache_filepath, 'r') as gmaps_cache_file:
            self.gmaps_cache = json.load(gmaps_cache_file)
        self.gmaps = googlemaps.Client(key=API_KEY)

    def geocode(self, name, address):
        key = f"{name} {address}"
        if key in self.gmaps_cache:
            print("geocode cache hit: ", key)
            return self.gmaps_cache[key]

        print("geocode cache miss: ", key)
        gmaps_result = self.gmaps.places(key)
        if gmaps_result:
            placeid = gmaps_result['results'][0]['place_id']
            location = gmaps_result[0]['geometry']['location']
            self.gmaps_cache[key] = (placeid, location['lat'], location['lng'])

            return (self.gmaps_cache[key])
        else:
            raise Exception(f"invalid key:{key}")

    def generate_google_maps_url(self, address, placeid):
        encoded_address = urllib.parse.quote(address)
        return f"https://www.google.com/maps/search/?api=1&query={encoded_address}&query_place_id={placeid}"

    def write_cache(self):
        with open(self.gmaps_cache_filepath, 'w') as file:
            json.dump(self.gmaps_cache, file)
