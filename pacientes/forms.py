# pacientes/forms.py
from django import forms
from .models import Paciente, Documento, Foto


class PacienteForm(forms.ModelForm):
    """Formulário para criar/editar pacientes"""
    
    data_nascimento = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = Paciente
        fields = [
            'nome_completo', 'data_nascimento', 'cpf', 'sexo',
            'telefone', 'email',
            'endereco', 'cidade', 'estado', 'cep',
            'tipo_sanguineo', 'alergias', 'medicamentos_uso',
            'historico_familiar', 'observacoes', 'ativo'
        ]
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2', 'placeholder': 'SP'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'tipo_sanguineo': forms.Select(attrs={'class': 'form-control'}),
            'alergias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medicamentos_uso': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'historico_familiar': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DocumentoForm(forms.ModelForm):
    """Formulário para upload de documentos PDF"""
    
    class Meta:
        model = Documento
        fields = ['titulo', 'descricao', 'arquivo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }


class FotoForm(forms.ModelForm):
    """Formulário para upload de fotos"""
    
    class Meta:
        model = Foto
        fields = ['titulo', 'descricao', 'imagem']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'imagem': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }