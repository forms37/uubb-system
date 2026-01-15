import pandas as pd
from django.http import HttpResponse


HEADERS = [
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
]


def descargar_plantilla_excel():
    df = pd.DataFrame(columns=HEADERS)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="plantilla_uubb.xlsx"'

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="UUBB")

    return response
