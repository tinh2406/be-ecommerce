class Roles:
    ADMIN: int = 1
    STAFF: int = 2
    CUSTOMER: int = 3

    CHOICES = (
        (ADMIN, "Admin"),
        (STAFF, "Staff"),
        (CUSTOMER, "Customer"),
    )

    DICT = dict(CHOICES)
