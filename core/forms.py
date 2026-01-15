from django import forms
from .models import OficinaRegional, Establecimiento

class ImportModo:
    POR_EML = "POR_EML"
    CONSOLIDADO = "CONSOLIDADO"

MODO_CHOICES = [
    (ImportModo.POR_EML, "Excel por EML (1 a 1)"),
    (ImportModo.CONSOLIDADO, "Excel consolidado (regional o nacional)"),
]

class ImportExcelForm(forms.Form):
    modo = forms.ChoiceField(choices=MODO_CHOICES)
    establecimiento = forms.ModelChoiceField(queryset=Establecimiento.objects.all(), required=False)
    oficina_regional = forms.ModelChoiceField(queryset=OficinaRegional.objects.all(), required=False)

    archivo = forms.FileField()

    # Solo aplicar “bajas por ausencia” si este excel es una foto completa del ámbito:
    aplicar_bajas = forms.BooleanField(required=False, initial=False)
class ExportExcelForm(forms.Form):
    estado = forms.ChoiceField(
        required=False,
        choices=[
            ("", "TODAS"),
            ("ACTIVA", "ACTIVA"),
            ("BAJA", "BAJA"),
        ],
    )
    oficina_regional = forms.ModelChoiceField(queryset=OficinaRegional.objects.all(), required=False)
    establecimiento = forms.ModelChoiceField(queryset=Establecimiento.objects.all(), required=False)
