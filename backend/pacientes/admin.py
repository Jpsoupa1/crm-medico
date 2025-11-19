from django.contrib import admin

from .models import Paciente, Documento, Foto


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'cpf', 'telefone', 'medico', 'data_cadastro', 'ativo']
    list_filter = ['ativo', 'sexo', 'data_cadastro']
    search_fields = ['nome_completo', 'cpf', 'telefone', 'email']
    date_hierarchy = 'data_cadastro'


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'paciente', 'data_upload']
    list_filter = ['data_upload']
    search_fields = ['titulo', 'paciente__nome_completo']


@admin.register(Foto)
class FotoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'paciente', 'data_upload']
    list_filter = ['data_upload']
    search_fields = ['titulo', 'paciente__nome_completo']