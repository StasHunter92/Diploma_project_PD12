from django.db import models
from django.utils import timezone


# ----------------------------------------------------------------------------------------------------------------------
# Create models
class DatesModelMixin(models.Model):
    """Abstract model for time-date conversion"""
    created = models.DateTimeField(verbose_name='Дата создания')
    updated = models.DateTimeField(verbose_name='Дата последнего обновления')

    class Meta:
        abstract: bool = True

    def save(self, *args, **kwargs) -> None:
        if not self.id:
            self.created = timezone.now()
        self.updated = timezone.now()
        return super().save(*args, **kwargs)
