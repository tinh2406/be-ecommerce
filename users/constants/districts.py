from json import load

with open('/Users/nguyeqoctih/Code/python/jobs/static/address/districts.json') as f:
    districts = load(f)


class Districts:
    CHOICES = [(district['code'], district['name']) for district in districts]

    def __init__(self, parent_code):
        self.CHOICES = [(district['code'], district['name']) for district in districts if district['parent_code'] == parent_code]
        self.DICT = {district['code']: district['name'] for district in districts}


