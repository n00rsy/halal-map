import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from titlecase import titlecase
from urllib3.util.retry import Retry


class Hmc:
    BASE_URL = 'https://halalhmc.org/outlets-by-name/'
    CATEGORY_NAMES = {
        'butchers': 'Butchers',
        'restaurants-and-takeaways': 'Restaurants and Takeaways',
        'caterers': 'Caterers',
        'dessert-shops': 'Dessert Shops',
        'other': 'Other',
    }

    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        self.session = self._new_session()

    def _new_session(self):
        session = requests.Session()
        session.headers.update(self.headers)
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=1,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=('GET',),
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        return session

    def _get_soup(self, url):
        response = self.session.get(url, timeout=(5, 15))
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

    def _normalise_text(self, text):
        text = re.sub(r'\s+', ' ', text).strip()
        return re.sub(r'\s+,', ',', text)

    def _get_page_urls(self, soup):
        last_page = 1
        last_link = soup.select_one('a.page-numbers.last')
        if last_link and last_link.get('href'):
            match = re.search(r'/page/(\d+)/', last_link['href'])
            if match:
                last_page = int(match.group(1))

        return [
            self.BASE_URL if page == 1 else urljoin(self.BASE_URL, f'page/{page}/')
            for page in range(1, last_page + 1)
        ]

    def _category_from_card(self, card):
        image = card.select_one('.outlet-title img')
        src = ''
        if image:
            src = image.get('data-src') or image.get('src') or ''

        match = re.search(r'cat-([a-z-]+)\.png', src)
        if not match:
            return ''

        slug = match.group(1)
        return self.CATEGORY_NAMES.get(slug, titlecase(slug.replace('-', ' ')))

    def _parse_card(self, card):
        title_link = card.select_one('.outlet-title a[href*="/outlets/"]')
        if not title_link:
            return None
        name = title_link.get_text(' ', strip=True)
        if 'non certified customer' in name.lower():
            return None

        address_node = card.select_one('.outlet-address')
        if not address_node:
            return None

        phone = ''
        phone_link = address_node.select_one('a.outlet-tel')
        if phone_link:
            phone = re.sub(r'^Tel:\s*', '', phone_link.get_text(strip=True))
            phone_link.decompose()

        address = self._normalise_text(address_node.get_text(' ', strip=True))
        if not address:
            return None

        source_url = urljoin(self.BASE_URL, title_link['href'])
        location = {
            'name': titlecase(name),
            'address': address,
            'phone': phone,
            'state': 'United Kingdom',
            'country': 'United Kingdom',
            'type': self._category_from_card(card),
            'certification': 'HMC',
            'source_url': source_url,
        }
        return location

    def _enrich_from_detail_page(self, location):
        response = self.session.get(location['source_url'], timeout=(5, 15))
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        marker = soup.select_one('.acf-map .marker')
        if marker:
            try:
                location['lat'] = float(marker['data-lat'])
                location['lng'] = float(marker['data-lng'])
            except (KeyError, TypeError, ValueError):
                pass

        status = soup.select_one('.current-status p')
        if status:
            location['status'] = self._normalise_text(status.get_text(' ', strip=True))

        category = soup.select_one('.category-name p')
        if category:
            location['type'] = self._normalise_text(category.get_text(' ', strip=True))

        detail_address = soup.select_one('.outlet-address-wrapper .outlet-address')
        if detail_address:
            address = self._normalise_text(detail_address.get_text(' ', strip=True))
            if address:
                location['address'] = address

        phone = soup.select_one('.outlet-number a[href^="tel:"]')
        if phone:
            location['phone'] = phone.get_text(strip=True)

        return location

    def get_all_resturaunts(self):
        print("Getting HMC certified listing...")
        first_page = self._get_soup(self.BASE_URL)
        page_urls = self._get_page_urls(first_page)
        print(f"Found {len(page_urls)} HMC listing pages")

        locations = []
        for page_number, page_url in enumerate(page_urls, start=1):
            soup = first_page if page_number == 1 else self._get_soup(page_url)
            cards = soup.select('.single-outlet-post.certified article')
            print(f"Found {len(cards)} HMC records on page {page_number}")

            for card in cards:
                location = self._parse_card(card)
                if not location:
                    continue
                locations.append(location)

        enriched_locations = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(self._enrich_from_detail_page, location): location
                for location in locations
            }
            for future in as_completed(futures):
                location = futures[future]
                try:
                    location = future.result()
                except Exception as e:
                    print(f"Error enriching HMC record {location['name']}: {e}")

                print(location['name'])
                enriched_locations.append(location)

        enriched_locations.sort(key=lambda location: location['name'].lower())
        return enriched_locations
