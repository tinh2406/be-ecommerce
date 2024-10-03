from json import load

with open('/Users/nguyeqoctih/Code/python/jobs/static/address/wards.json') as f:
    wards = load(f)


class Wards:
    CHOICES = [(ward['code'], ward['name']) for ward in wards]

    def __init__(self, parent_code):
        self.CHOICES = [(ward['code'], ward['name']) for ward in wards if ward['parent_code'] == parent_code]
        self.DICT = {ward['code']: {
            'name': ward['name'],
            'path_with_type': ward['path_with_type'],
        } for ward in wards}


