from django.db import models
class OficinaRegional(models.Model):
    nombre=models.CharField(max_length=150,unique=True)
class Establecimiento(models.Model):
    nombre=models.CharField(max_length=200,unique=True)
    oficina_regional=models.ForeignKey(OficinaRegional,on_delete=models.PROTECT)
class UUBB(models.Model):
    codigo_uubb=models.CharField(max_length=50,unique=True)
    nombre_razon_social=models.CharField(max_length=255,blank=True)
    establecimiento=models.ForeignKey(Establecimiento,on_delete=models.PROTECT)
