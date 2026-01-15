import pandas as pd
from django.utils import timezone
from django.utils.dateparse import parse_date

TEXT_FILL = "SIN INFORMACIÓN"

COL_MAP = {
    "CÓDIGO DE UUBB": "codigo_uubb",
    "NOMBRE O RAZON SOCIAL DE LA UUBB": "nombre_razon_social",
    "DIRECCIÓN": "direccion",
    "DEPARTAMENTO": "departamento",
    "PROVINCIA": "provincia",
    "DISTRITO": "distrito",
    "DÍAS Y HORARIOS DE ATENCIÓN": "dias_horarios",
    "NOMBRE DE EML": "nombre_eml",
    "OFICINA REGIONAL": "oficina_regional_txt",
    "RESOLUCIÓN DIRECTORAL": "resolucion_directoral",
    "FECHA DE RD": "fecha_rd",
    "AUTORIDAD DELEGADA": "autoridad_delegada",
    "FECHA DE ACTA DE INSCRIPCIÓN": "fecha_acta_inscripcion",
    "TIPO": "tipo",
    "DESAGREGADO": "desagregado",
    "ÁREA DONDE PRESTA LOS SERVICIOS": "area_servicios",
    "N° CAPACIDAD DE ATENCIÓN": "capacidad_atencion",
    "VACANTES DISPONIBLES PARA UBICAR": "vacantes_disponibles",
    "CANTIDAD DE SENTENCIADOS CON JORNADAS CUMPLIDAS": "sentenciados_jornadas_cumplidas",
    "SITUACIÓN DE UNA UUBB": "situacion_uubb",
    "NOMBRE DEL RESPONSABLE": "nombre_responsable",
    "CORREO": "correo",
    "TELÉFONO": "telefono",
    "SUPERVISOR A CARGO": "supervisor",
    "FECHA DE EVALUACIÓN DEL DESEMPEÑO": "fecha_evaluacion",
}

DATE_FIELDS = {"fecha_rd", "fecha_acta_inscripcion", "fecha_evaluacion"}
INT_FIELDS = {"capacidad_atencion", "vacantes_disponibles", "sentenciados_jornadas_cumplidas"}

def _norm_str(x):
    if pd.isna(x):
        return ""
    return str(x).strip()

def _norm_int(x):
    if pd.isna(x) or str(x).strip() == "":
        return None
    try:
        return int(float(str(x).strip()))
    except Exception:
        return None

def _norm_date(x):
    if pd.isna(x) or str(x).strip() == "":
        return None
    if isinstance(x, pd.Timestamp):
        return x.date()
    s = str(x).strip()
    d = parse_date(s)
    if d:
        return d
    try:
        return pd.to_datetime(s, dayfirst=True).date()
    except Exception:
        return None

def read_uubb_excel(fileobj, sheet_name="UUBB"):
    # Lee sin header y busca la fila donde está "CÓDIGO DE UUBB"
    raw = pd.read_excel(fileobj, sheet_name=sheet_name, header=None, dtype=str)
    header_row = None
    for i in range(min(len(raw), 120)):
        row = raw.iloc[i].astype(str).str.strip()
        if (row.str.upper() == "CÓDIGO DE UUBB").any():
            header_row = i
            break
    if header_row is None:
        raise ValueError("No se encontró el encabezado 'CÓDIGO DE UUBB' en la hoja UUBB.")

    headers = raw.iloc[header_row].tolist()
    df = raw.iloc[header_row + 1:].copy()
    df.columns = headers
    df = df.dropna(how="all")

    # Quedarnos solo con columnas conocidas
    df = df[[c for c in df.columns if c in COL_MAP]].rename(columns=COL_MAP)

    # Normalización por tipo
    for col in df.columns:
        if col in DATE_FIELDS:
            df[col] = df[col].apply(_norm_date)
        elif col in INT_FIELDS:
            df[col] = df[col].apply(_norm_int)
        else:
            df[col] = df[col].apply(_norm_str)

    # Código obligatorio
    if "codigo_uubb" not in df.columns:
        raise ValueError("Falta la columna 'CÓDIGO DE UUBB'.")

    df["codigo_uubb"] = df["codigo_uubb"].apply(_norm_str)
    df = df[df["codigo_uubb"] != ""]

    return df

def fill_text_fields(row_dict):
    # Solo para textos; fechas/números se quedan None si están vacíos
    for k, v in list(row_dict.items()):
        if k in DATE_FIELDS or k in INT_FIELDS:
            continue
        if v is None or (isinstance(v, str) and v.strip() == ""):
            row_dict[k] = TEXT_FILL
    return row_dict

def apply_bajas_por_ausencia(qs_uubb_ambito, codigos_vistos, motivo="Ausente en Excel (foto completa)"):
    hoy = timezone.localdate()
    for u in qs_uubb_ambito.exclude(codigo_uubb__in=codigos_vistos).filter(estado="ACTIVA"):
        u.estado = "BAJA"
        u.fecha_baja = hoy
        u.motivo_baja = motivo
        u.save()
