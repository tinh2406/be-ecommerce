class Genders:
    MALE: int = 1
    FEMALE: int = 2
    OTHER: int = 3

    CHOICES = (
        (MALE, 'male'),
        (FEMALE, 'female'),
        (OTHER, 'other')
    )

    DICT = dict(CHOICES)
