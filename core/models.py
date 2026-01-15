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
    class Estado(models.TextChoices):
        ACTIVA = "ACTIVA", "Activa"
        BAJA = "BAJA", "Baja"

    # Identificación
    codigo_uubb = models.CharField(max_length=50)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.PROTECT)

    # Datos principales
    nombre_razon_social = models.CharField(max_length=255, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    departamento = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    distrito = models.CharField(max_length=100, blank=True)
    dias_horarios = models.CharField(max_length=255, blank=True)
    nombre_eml = models.CharField(max_length=200, blank=True)          # Se llena desde Excel si viene
    oficina_regional_txt = models.CharField(max_length=150, blank=True)  # Se llena desde Excel si viene

    # Documentos
    resolucion_directoral = models.CharField(max_length=100, blank=True)
    fecha_rd = models.DateField(null=True, blank=True)
    autoridad_delegada = models.CharField(max_length=150, blank=True)
    fecha_acta_inscripcion = models.DateField(null=True, blank=True)

    # Clasificación
    tipo = models.CharField(max_length=100, blank=True)
    desagregado = models.CharField(max_length=100, blank=True)
    area_servicios = models.CharField(max_length=150, blank=True)

    # Números (permiten NULL: si no informan)
    capacidad_atencion = models.IntegerField(null=True, blank=True)
    vacantes_disponibles = models.IntegerField(null=True, blank=True)
    sentenciados_jornadas_cumplidas = models.IntegerField(null=True, blank=True)

    situacion_uubb = models.CharField(max_length=100, blank=True)

    # Contacto / supervisión
    nombre_responsable = models.CharField(max_length=150, blank=True)
    correo = models.CharField(max_length=150, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    supervisor = models.CharField(max_length=150, blank=True)
    fecha_evaluacion = models.DateField(null=True, blank=True)

    # Campos internos del sistema (NO vienen en Excel)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ACTIVA)
    fecha_baja = models.DateField(null=True, blank=True)
    motivo_baja = models.CharField(max_length=255, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("establecimiento", "codigo_uubb")

    def __str__(self):
        base = self.codigo_uubb
        if self.nombre_razon_social:
            base += f" - {self.nombre_razon_social}"
        return base
