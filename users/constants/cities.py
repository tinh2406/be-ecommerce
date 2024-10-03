from json import load

with open('/Users/nguyeqoctih/Code/python/jobs/static/address/cities.json') as f:
    cities = load(f)

class Cities:

    CHOICES = [(city['code'], city['name']) for city in cities]

    DICT = {city['code']: city['name'] for city in cities}