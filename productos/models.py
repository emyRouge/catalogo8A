from django.db import models

class Productos(models.Model):
    name = models.CharField(max_length=100, unique=True)
    precio = models.FloatField(null=True, blank=True)
    descripcion = models.CharField(max_length=100)
    stock = models.IntegerField(null=True, blank=True)
   
