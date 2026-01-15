from django.db import models


class OficinaRegional(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre or f"OficinaRegional {self.pk}"

class Establecimiento(models.Model):
    nombre = models.CharField(max_length=255)
    oficina_regional = models.ForeignKey(OficinaRegional, on_delete=models.PROTECT)

    def __str__(self):
        # Nunca asumas que existe nombre
        return self.nombre or f"EML {self.pk}"


class UUBB(models.Model):
    codigo_uubb = models.CharField(max_length=50)
    nombre_razon_social = models.CharField(max_length=255, blank=True, null=True)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.PROTECT)

    def __str__(self):
        # Evita concatenar None
        nom = self.nombre_razon_social or ""
        cod = self.codigo_uubb or f"UUBB {self.pk}"
        return f"{cod} {nom}".strip()

class Estado(models.TextChoices):
    ACTIVA = "ACTIVA", "Activa"
    BAJA = "BAJA", "Baja"

class UUBB(models.Model):
    # Identificación
    codigo_uubb = models.CharField(max_length=50)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.PROTECT)

    # Datos principales
    nombre_razon_social = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True)
    departamento = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    distrito = models.CharField(max_length=100, blank=True)
    dias_horarios = models.CharField(max_length=255, blank=True)
    nombre_eml = models.CharField(max_length=200, blank=True)
    oficina_regional_txt = models.CharField(max_length=150, blank=True)

    # Resoluciones / fechas
    resolucion_directoral = models.CharField(max_length=100, blank=True)
    fecha_rd = models.DateField(null=True, blank=True)
    autoridad_delegada = models.CharField(max_length=150, blank=True)
    fecha_acta_inscripcion = models.DateField(null=True, blank=True)

    # Clasificación
    tipo = models.CharField(max_length=100, blank=True)
    desagregado = models.CharField(max_length=100, blank=True)
    area_servicios = models.CharField(max_length=150, blank=True)

    # Números
    capacidad_atencion = models.IntegerField(null=True, blank=True)
    vacantes_disponibles = models.IntegerField(null=True, blank=True)
    sentenciados_jornadas_cumplidas = models.IntegerField(null=True, blank=True)

    # Estado / control
    situacion_uubb = models.CharField(max_length=100, blank=True)
    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.ACTIVA
    )
    fecha_baja = models.DateField(null=True, blank=True)
    motivo_baja = models.CharField(max_length=255, blank=True)

    # Contacto
    nombre_responsable = models.CharField(max_length=150, blank=True)
    correo = models.CharField(max_length=150, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    supervisor = models.CharField(max_length=150, blank=True)
    fecha_evaluacion = models.DateField(null=True, blank=True)

    # Sistema
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("establecimiento", "codigo_uubb")

    def __str__(self):
        nom = self.nombre_razon_social or ""
        cod = self.codigo_uubb or f"UUBB {self.pk}"
        return f"{cod} - {nom}".strip()

