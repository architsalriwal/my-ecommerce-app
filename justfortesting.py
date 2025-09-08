from django.db import models

class Users(models.Model):
    id = models.PositiveIntegerField(blank = False, null = False , unique = True)
    username = models.CharField(blank = False, unique = True, null = False)
    email = models.EmailField(blank = False, unique = True, null = False)
    

