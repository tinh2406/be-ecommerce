from django.db import models
from django.utils import timezone


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        self.deleted_at = timezone.now()
        return self.save()

    def restore(self):
        self.deleted_at = None
        return self.save()

    class Meta:
        abstract = True
