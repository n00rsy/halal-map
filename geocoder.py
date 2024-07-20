
import googlemaps

class Geocoder:
    def __init__(self, API_KEY):
        # Google Maps API Key

        self.gmaps = googlemaps.Client(key=API_KEY)

    def geocode(self, address):
            geocode_result = self.gmaps.geocode(address)

            if geocode_result:
                # Extracting the location details
                location = geocode_result[0]['geometry']['location']
                lat = location['lat']
                lng = location['lng']
                return (lat, lng)
            else:
                raise Exception(f"invalid address:{address}")
