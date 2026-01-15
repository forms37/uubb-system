from django.db import models
class OficinaRegional(models.Model):
    nombre = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.nombre


class Establecimiento(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    oficina_regional = models.ForeignKey(OficinaRegional, on_delete=models.PROTECT)

    def __str__(self):
        return self.nombre


class UUBB(models.Model):
    codigo_uubb = models.CharField(max_length=50, unique=True)
    nombre_razon_social = models.CharField(max_length=255, blank=True)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.PROTECT)

    def __str__(self):
        # Muestra código + nombre si existe
        if self.nombre_razon_social:
            return f"{self.codigo_uubb} - {self.nombre_razon_social}"
        return self.codigo_uubb
