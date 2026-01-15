from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
from django.db import transaction

from .models import OficinaRegional, Establecimiento, UUBB
from .forms import ImportExcelForm, ImportModo
from .importer import read_uubb_excel, fill_text_fields, apply_bajas_por_ausencia
from .template_excel import descargar_plantilla_excel 

@admin.register(OficinaRegional)
class OficinaRegionalAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Establecimiento)
class EstablecimientoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "oficina_regional")
    list_filter = ("oficina_regional",)
    search_fields = ("nombre",)


@admin.register(UUBB)
class UUBBAdmin(admin.ModelAdmin):
    list_display = ("codigo_uubb", "nombre_razon_social", "establecimiento", "estado", "vacantes_disponibles", "supervisor")
    list_filter = ("estado", "establecimiento", "establecimiento__oficina_regional")
    search_fields = ("codigo_uubb", "nombre_razon_social", "supervisor", "distrito")


class ImportAdminView(admin.AdminSite):
    pass


# Agregamos una vista custom dentro del Admin
def import_excel_view(request):
    if request.method == "POST":
        form = ImportExcelForm(request.POST, request.FILES)
        if form.is_valid():
            modo = form.cleaned_data["modo"]
            est = form.cleaned_data.get("establecimiento")
            ofr = form.cleaned_data.get("oficina_regional")
            archivo = form.cleaned_data["archivo"]
            aplicar_bajas = form.cleaned_data["aplicar_bajas"]

            try:
                df = read_uubb_excel(archivo, sheet_name="UUBB")
            except Exception as e:
                messages.error(request, f"Error leyendo Excel: {e}")
                return redirect("..")

            created = 0
            updated = 0
            errores = 0

            codigos_vistos_por_ambito = {}  # clave: establecimiento_id -> set(codigos)

            with transaction.atomic():
                for _, row in df.iterrows():
                    data = row.to_dict()
                    data = fill_text_fields(data)

                    codigo = data.get("codigo_uubb", "").strip()
                    if not codigo:
                        continue

                    # Determinar establecimiento destino
                    if modo == ImportModo.POR_EML:
                        if not est:
                            mensajes = "En modo 'por EML' debes seleccionar un Establecimiento."
                            messages.error(request, mensajes)
                            return redirect("..")
                        est_dest = est
                    else:
                        # CONSOLIDADO: necesita NOMBRE DE EML en el Excel
                        nombre_eml = data.get("nombre_eml", "").strip()
                        if not nombre_eml or nombre_eml == "SIN INFORMACIÓN":
                            errores += 1
                            continue
                        try:
                            est_dest = Establecimiento.objects.get(nombre__iexact=nombre_eml)
                        except Establecimiento.DoesNotExist:
                            # Si seleccionaste oficina regional, podemos rechazar si no pertenece
                            errores += 1
                            continue

                        # Si el usuario seleccionó una oficina regional, validar que el EML pertenezca a esa OR
                        if ofr and est_dest.oficina_regional_id != ofr.id:
                            errores += 1
                            continue

                    codigos_vistos_por_ambito.setdefault(est_dest.id, set()).add(codigo)

                    defaults = {
                        "nombre_razon_social": data.get("nombre_razon_social", ""),
                        "direccion": data.get("direccion", ""),
                        "departamento": data.get("departamento", ""),
                        "provincia": data.get("provincia", ""),
                        "distrito": data.get("distrito", ""),
                        "dias_horarios": data.get("dias_horarios", ""),
                        "nombre_eml": data.get("nombre_eml", ""),
                        "oficina_regional_txt": data.get("oficina_regional_txt", ""),
                        "resolucion_directoral": data.get("resolucion_directoral", ""),
                        "fecha_rd": data.get("fecha_rd"),
                        "autoridad_delegada": data.get("autoridad_delegada", ""),
                        "fecha_acta_inscripcion": data.get("fecha_acta_inscripcion"),
                        "tipo": data.get("tipo", ""),
                        "desagregado": data.get("desagregado", ""),
                        "area_servicios": data.get("area_servicios", ""),
                        "capacidad_atencion": data.get("capacidad_atencion"),
                        "vacantes_disponibles": data.get("vacantes_disponibles"),
                        "sentenciados_jornadas_cumplidas": data.get("sentenciados_jornadas_cumplidas"),
                        "situacion_uubb": data.get("situacion_uubb", ""),
                        "nombre_responsable": data.get("nombre_responsable", ""),
                        "correo": data.get("correo", ""),
                        "telefono": data.get("telefono", ""),
                        "supervisor": data.get("supervisor", ""),
                        "fecha_evaluacion": data.get("fecha_evaluacion"),
                        # Si reaparece, lo reactivamos:
                        "estado": "ACTIVA",
                        "fecha_baja": None,
                        "motivo_baja": "",
                    }

                    obj, was_created = UUBB.objects.update_or_create(
                        establecimiento=est_dest,
                        codigo_uubb=codigo,
                        defaults=defaults
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1

                # Bajas por ausencia SOLO si el usuario marcó que el Excel es foto completa
                if aplicar_bajas:
                    if modo == ImportModo.POR_EML and est:
                        qs = UUBB.objects.filter(establecimiento=est)
                        apply_bajas_por_ausencia(qs, codigos_vistos_por_ambito.get(est.id, set()))
                    elif modo == ImportModo.CONSOLIDADO and ofr:
                        # Foto completa regional: aplicar por cada EML de esa OR
                        for e in Establecimiento.objects.filter(oficina_regional=ofr):
                            qs = UUBB.objects.filter(establecimiento=e)
                            apply_bajas_por_ausencia(qs, codigos_vistos_por_ambito.get(e.id, set()),
                                                     motivo="Ausente en Excel (foto completa regional)")
                    elif modo == ImportModo.CONSOLIDADO and not ofr:
                        # Foto completa nacional: aplicar por cada EML
                        for e in Establecimiento.objects.all():
                            qs = UUBB.objects.filter(establecimiento=e)
                            apply_bajas_por_ausencia(qs, codigos_vistos_por_ambito.get(e.id, set()),
                                                     motivo="Ausente en Excel (foto completa nacional)")

            messages.success(
                request,
                f"Importación completada. Nuevas: {created}, Actualizadas: {updated}, Filas con error/EML no encontrado: {errores}."
            )
            return redirect("/admin/core/uubb/")

    else:
        form = ImportExcelForm()

    return render(request, "admin/import_excel.html", {"form": form})


# Inyectar la URL dentro del admin (en el admin site por defecto)
def get_admin_urls(urls):
    def get_urls():
        return [
            path(
                "importar-excel/plantilla/",
                admin.site.admin_view(lambda request: descargar_plantilla_excel()),
                name="descargar_plantilla_excel",
            ),
            path(
                "importar-excel/",
                admin.site.admin_view(import_excel_view),
                name="importar_excel",
            ),
        ] + urls
    return get_urls


admin.site.get_urls = get_admin_urls(admin.site.get_urls())
