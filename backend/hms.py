import requests
from bs4 import BeautifulSoup
from titlecase import titlecase


class Hms:
    def __init__(self, driver):
        self.driver = driver

    def get_all_resturaunts(self):
        print("Getting HMS certified listing...")
        response = requests.get(
            'https://hmsusa.org/certified-listing',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr', class_='record-table-list')
        print(f"Found {len(rows)} records")

        locations = []
        for row in rows:
            if row.get('data-category') != 'Restaurants':
                continue

            cells = row.find_all('td')
            if len(cells) < 6:
                continue

            # Products: tooltip text on each icon-tooltip span in the Products cell
            products_cell = next(
                (c for c in cells if c.get('data-title') == 'Products'), None
            )
            products = []
            if products_cell:
                for span in products_cell.find_all('span', class_='icon-tooltip'):
                    tooltip = span.get('data-tooltip', '').strip()
                    if tooltip:
                        products.append(tooltip)

            # Expiry: text in the "Expire at" cell
            expire_cell = next(
                (c for c in cells if c.get('data-title') == 'Expire at'), None
            )
            expires = expire_cell.get_text(strip=True) if expire_cell else ''

            # Phone: strip icon/link, grab the text node
            phone_cell = next(
                (c for c in cells if c.get('data-title') == 'Phone'), None
            )
            phone = ''
            if phone_cell:
                phone = phone_cell.get_text(strip=True)

            location = {
                'name': titlecase(row.get('data-name', '')).strip(),
                'address': row.get('data-address', ''),
                'phone': phone,
                'state': row.get('data-state-name', ''),
                'products': products,
                'expires': expires,
                'certification': 'HMS',
            }
            print(location['name'])
            locations.append(location)

        return locations
