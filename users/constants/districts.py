from json import load

from core.settings import BASE_DIR

with open(f'{BASE_DIR}/static/address/districts.json') as f:
    districts = load(f)


class Districts:
    CHOICES = [(district['code'], district['name']) for district in districts]

    def __init__(self, parent_code):
        self.CHOICES = [(district['code'], district['name']) for district in districts if district['parent_code'] == parent_code]
        self.DICT = {district['code']: district['name'] for district in districts}


