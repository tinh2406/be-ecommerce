from json import load

from core.settings import BASE_DIR

with open(f'{BASE_DIR}/static/address/cities.json') as f:
    cities = load(f)

class Cities:

    CHOICES = [(city['code'], city['name']) for city in cities]

    DICT = {city['code']: city['name'] for city in cities}