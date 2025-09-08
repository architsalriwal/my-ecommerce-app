# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\base\models.py

from django.db import models
import uuid

class BaseModel(models.Model):
    # Use UUID as the primary key for better scalability and security
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True # This means it won't create a separate table in the database
        ordering = ['-created_at'] # Default ordering for all models inheriting from this