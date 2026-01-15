import pandas as pd
from django.http import HttpResponse


EXPORT_HEADERS = [
    "CÓDIGO DE UUBB",
    "NOMBRE O RAZON SOCIAL DE LA UUBB",
    "DIRECCIÓN",
    "DEPARTAMENTO",
    "PROVINCIA",
    "DISTRITO",
    "DÍAS Y HORARIOS DE ATENCIÓN",
    "NOMBRE DE EML",
    "OFICINA REGIONAL",
    "RESOLUCIÓN DIRECTORAL",
    "FECHA DE RD",
    "AUTORIDAD DELEGADA",
    "FECHA DE ACTA DE INSCRIPCIÓN",
    "TIPO",
    "DESAGREGADO",
    "ÁREA DONDE PRESTA LOS SERVICIOS",
    "N° CAPACIDAD DE ATENCIÓN",
    "VACANTES DISPONIBLES PARA UBICAR",
    "CANTIDAD DE SENTENCIADOS CON JORNADAS CUMPLIDAS",
    "SITUACIÓN DE UNA UUBB",
    "NOMBRE DEL RESPONSABLE",
    "CORREO",
    "TELÉFONO",
    "SUPERVISOR A CARGO",
    "FECHA DE EVALUACIÓN DEL DESEMPEÑO",
    "ESTADO",
    "FECHA BAJA",
    "MOTIVO BAJA",
]


def export_uubb_to_excel(qs, filename="export_uubb.xlsx"):
    """
    Recibe un QuerySet de UUBB y devuelve un archivo Excel descargable.
    """
    rows = []
    for u in qs.select_related("establecimiento", "establecimiento__oficina_regional"):
        rows.append({
            "CÓDIGO DE UUBB": u.codigo_uubb,
            "NOMBRE O RAZON SOCIAL DE LA UUBB": u.nombre_razon_social,
            "DIRECCIÓN": u.direccion,
            "DEPARTAMENTO": u.departamento,
            "PROVINCIA": u.provincia,
            "DISTRITO": u.distrito,
            "DÍAS Y HORARIOS DE ATENCIÓN": u.dias_horarios,
            "NOMBRE DE EML": u.establecimiento.nombre,
            "OFICINA REGIONAL": u.establecimiento.oficina_regional.nombre,
            "RESOLUCIÓN DIRECTORAL": u.resolucion_directoral,
            "FECHA DE RD": u.fecha_rd,
            "AUTORIDAD DELEGADA": u.autoridad_delegada,
            "FECHA DE ACTA DE INSCRIPCIÓN": u.fecha_acta_inscripcion,
            "TIPO": u.tipo,
            "DESAGREGADO": u.desagregado,
            "ÁREA DONDE PRESTA LOS SERVICIOS": u.area_servicios,
            "N° CAPACIDAD DE ATENCIÓN": u.capacidad_atencion,
            "VACANTES DISPONIBLES PARA UBICAR": u.vacantes_disponibles,
            "CANTIDAD DE SENTENCIADOS CON JORNADAS CUMPLIDAS": u.sentenciados_jornadas_cumplidas,
            "SITUACIÓN DE UNA UUBB": u.situacion_uubb,
            "NOMBRE DEL RESPONSABLE": u.nombre_responsable,
            "CORREO": u.correo,
            "TELÉFONO": u.telefono,
            "SUPERVISOR A CARGO": u.supervisor,
            "FECHA DE EVALUACIÓN DEL DESEMPEÑO": u.fecha_evaluacion,
            "ESTADO": u.estado,
            "FECHA BAJA": u.fecha_baja,
            "MOTIVO BAJA": u.motivo_baja,
        })

    df = pd.DataFrame(rows, columns=EXPORT_HEADERS)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="UUBB")

    return response
