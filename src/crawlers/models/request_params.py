import uuid

from django.db.models import JSONField, UUIDField

from core.models import BaseTimeModel


class RequestParams(BaseTimeModel):

    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    params = JSONField(default=dict)
    headers = JSONField(default=dict)

    cache_key_fields = ["id"]
    key = "request_params_"

    class Meta:
        ordering = ["-created_at"]
        db_table = "request_params"
        app_label = "crawlers"
