from django.db.models import Count, Sum, Q
from .models import UUBB


def kpis(qs):
    """
    qs: QuerySet de UUBB ya filtrado (por OR/EML/estado).
    """
    total = qs.count()
    activas = qs.filter(estado="ACTIVA").count()
    bajas = qs.filter(estado="BAJA").count()

    # Sumatorias solo donde hay dato (NULL no suma)
    total_vacantes = qs.aggregate(s=Sum("vacantes_disponibles"))["s"] or 0
    total_capacidad = qs.aggregate(s=Sum("capacidad_atencion"))["s"] or 0

    sin_vacantes_dato = qs.filter(vacantes_disponibles__isnull=True).count()
    sin_tipo = qs.filter(Q(tipo__isnull=True) | Q(tipo="") | Q(tipo="SIN INFORMACIÓN")).count()

    # Alertas
    vacantes_mayor_capacidad = qs.filter(
        vacantes_disponibles__isnull=False,
        capacidad_atencion__isnull=False,
        vacantes_disponibles__gt=Q("capacidad_atencion"),
    ).count()

    return {
        "total": total,
        "activas": activas,
        "bajas": bajas,
        "total_vacantes": total_vacantes,
        "total_capacidad": total_capacidad,
        "sin_vacantes_dato": sin_vacantes_dato,
        "sin_tipo": sin_tipo,
        "vacantes_mayor_capacidad": vacantes_mayor_capacidad,
    }


def por_oficina_regional(qs):
    return list(
        qs.values("establecimiento__oficina_regional__nombre")
        .annotate(
            total=Count("id"),
            activas=Count("id", filter=Q(estado="ACTIVA")),
            bajas=Count("id", filter=Q(estado="BAJA")),
            vacantes=Sum("vacantes_disponibles"),
            capacidad=Sum("capacidad_atencion"),
            sin_vacantes=Count("id", filter=Q(vacantes_disponibles__isnull=True)),
        )
        .order_by("establecimiento__oficina_regional__nombre")
    )


def por_establecimiento(qs):
    return list(
        qs.values("establecimiento__nombre", "establecimiento__oficina_regional__nombre")
        .annotate(
            total=Count("id"),
            activas=Count("id", filter=Q(estado="ACTIVA")),
            bajas=Count("id", filter=Q(estado="BAJA")),
            vacantes=Sum("vacantes_disponibles"),
            capacidad=Sum("capacidad_atencion"),
            sin_vacantes=Count("id", filter=Q(vacantes_disponibles__isnull=True)),
        )
        .order_by("establecimiento__oficina_regional__nombre", "establecimiento__nombre")
    )


def por_tipo(qs):
    return list(
        qs.values("tipo")
        .annotate(
            total=Count("id"),
            activas=Count("id", filter=Q(estado="ACTIVA")),
            bajas=Count("id", filter=Q(estado="BAJA")),
        )
        .order_by("tipo")
    )


def matriz_or_tipo(qs):
    """
    Devuelve filas por (OR, tipo) y luego en la plantilla se arma una matriz.
    """
    return list(
        qs.values("establecimiento__oficina_regional__nombre", "tipo")
        .annotate(
            total=Count("id"),
            activas=Count("id", filter=Q(estado="ACTIVA")),
            bajas=Count("id", filter=Q(estado="BAJA")),
        )
        .order_by("establecimiento__oficina_regional__nombre", "tipo")
    )


def matriz_eml_tipo(qs):
    """
    Matriz EML x Tipo (con 40 EML es manejable).
    """
    return list(
        qs.values("establecimiento__nombre", "tipo")
        .annotate(
            total=Count("id"),
            activas=Count("id", filter=Q(estado="ACTIVA")),
            bajas=Count("id", filter=Q(estado="BAJA")),
        )
        .order_by("establecimiento__nombre", "tipo")
    )
