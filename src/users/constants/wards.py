from json import load

from core.settings import BASE_DIR

with open(f"{BASE_DIR}/static/address/wards.json") as f:
    wards = load(f)


class Wards:
    CHOICES = [(ward["code"], ward["name"]) for ward in wards]

    def __init__(self, parent_code):
        self.CHOICES = [
            (ward["code"], ward["name"])
            for ward in wards
            if ward["parent_code"] == parent_code
        ]
        self.DICT = {
            ward["code"]: {
                "name": ward["name"],
                "path_with_type": ward["path_with_type"],
            }
            for ward in wards
        }
