from statistics.utils import get_date_ranges

from django.db.models import Case, Count, JSONField, Value, When

from products.models import Product


class ProductStatisticsDomain:

    @classmethod
    def get_product_statistics(cls, query: dict):

        cycle = query.get("cycle")
        num_cycle = query.get("num_cycle")
        start_date = query.get("start_date")
        end_date = query.get("end_date")

        dates_ranges = get_date_ranges(cycle, num_cycle, start_date, end_date)

        conditions = [
            When(
                created_at__range=(dates_ranges[i + 1], dates_ranges[i]),
                then=Value(f"{dates_ranges[i+1].strftime('%Y-%m-%d')}"),
            )
            for i in range(len(dates_ranges) - 1)
        ]

        query_set = (
            Product.objects.annotate(
                range_label=Case(
                    *conditions, default=Value("0"), output_field=JSONField()
                )
            )
            .values("range_label")
            .annotate(count=Count("range_label"))
            .order_by("range_label")
        )

        return [item for item in query_set]
