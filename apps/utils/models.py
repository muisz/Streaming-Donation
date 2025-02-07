from django.db import models


class BaseModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
