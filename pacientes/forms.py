# pacientes/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
import re
from .models import Paciente, Documento, Foto


def validar_cpf(cpf):
    """Valida CPF usando algoritmo oficial"""
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais (ex: 111.111.111-11)
    if cpf == cpf[0] * 11:
        return False
    
    # Valida primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[9]) != digito1:
        return False
    
    # Valida segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[10]) != digito2:
        return False
    
    return True


class PacienteForm(forms.ModelForm):
    """Formulário para criar/editar pacientes com validações"""
    
    data_nascimento = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'max': date.today().isoformat()  # Não permite datas futuras
        }),
        label='Data de Nascimento'
    )
    
    cpf = forms.CharField(
        max_length=14,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '000.000.000-00',
            'id': 'id_cpf',
            'maxlength': '14'
        }),
        label='CPF'
    )
    
    cep = forms.CharField(
        max_length=9,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '00000-000',
            'id': 'id_cep',
            'maxlength': '9'
        }),
        label='CEP'
    )
    
    telefone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(00) 00000-0000',
            'id': 'id_telefone',
            'maxlength': '15'
        }),
        label='Telefone'
    )
    
    class Meta:
        model = Paciente
        fields = [
            'nome_completo', 'data_nascimento', 'cpf', 'sexo',
            'telefone', 'email',
            'cep', 'endereco', 'cidade', 'estado',
            'tipo_sanguineo', 'alergias', 'medicamentos_uso',
            'historico_familiar', 'observacoes', 'ativo'
        ]
        widgets = {
            'nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo',
                'id': 'id_nome_completo'
            }),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_endereco',
                'readonly': 'readonly'  # Preenchido automaticamente
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_cidade',
                'readonly': 'readonly'  # Preenchido automaticamente
            }),
            'estado': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '2',
                'id': 'id_estado',
                'readonly': 'readonly'  # Preenchido automaticamente
            }),
            'tipo_sanguineo': forms.Select(attrs={'class': 'form-control'}),
            'alergias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medicamentos_uso': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'historico_familiar': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_nome_completo(self):
        """Valida que o nome contenha apenas letras e espaços"""
        nome = self.cleaned_data.get('nome_completo', '')
        
        # Remove espaços extras
        nome = ' '.join(nome.split())
        
        # Verifica se contém apenas letras e espaços
        if not re.match(r'^[A-Za-zÀ-ÿ\s]+$', nome):
            raise ValidationError('O nome deve conter apenas letras.')
        
        # Verifica se tem pelo menos nome e sobrenome
        if len(nome.split()) < 2:
            raise ValidationError('Por favor, informe o nome completo (nome e sobrenome).')
        
        return nome.title()  # Capitaliza cada palavra
    
    def clean_cpf(self):
        """Valida CPF"""
        cpf = self.cleaned_data.get('cpf', '')
        
        # Remove caracteres não numéricos
        cpf_numeros = re.sub(r'[^0-9]', '', cpf)
        
        # Verifica quantidade de caracteres
        if len(cpf_numeros) != 11:
            raise ValidationError('O CPF deve conter exatamente 11 dígitos.')
        
        # Valida CPF usando algoritmo oficial
        if not validar_cpf(cpf_numeros):
            raise ValidationError('CPF inválido. Por favor, verifique os números digitados.')
        
        # Formata CPF: 000.000.000-00
        cpf_formatado = f'{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}'
        
        # Verifica se CPF já existe (exceto para edição)
        if self.instance.pk:
            # Está editando
            if Paciente.objects.filter(cpf=cpf_formatado).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Este CPF já está cadastrado para outro paciente.')
        else:
            # Está criando novo
            if Paciente.objects.filter(cpf=cpf_formatado).exists():
                raise ValidationError('Este CPF já está cadastrado.')
        
        return cpf_formatado
    
    def clean_telefone(self):
        """Valida telefone com DDD (11 dígitos)"""
        telefone = self.cleaned_data.get('telefone', '')
        
        # Remove caracteres não numéricos
        telefone_numeros = re.sub(r'[^0-9]', '', telefone)
        
        # Verifica se tem exatamente 11 dígitos
        if len(telefone_numeros) != 11:
            raise ValidationError('O telefone deve conter exatamente 11 dígitos (DDD + número).')
        
        # Verifica se começa com DDD válido (11-99)
        ddd = int(telefone_numeros[:2])
        if ddd < 11 or ddd > 99:
            raise ValidationError('DDD inválido. Use o formato: (DD) 9XXXX-XXXX')
        
        # Verifica se é celular (9º dígito deve ser 9)
        if telefone_numeros[2] != '9':
            raise ValidationError('Número de celular inválido. O 3º dígito deve ser 9.')
        
        # Formata: (00) 90000-0000
        telefone_formatado = f'({telefone_numeros[:2]}) {telefone_numeros[2:7]}-{telefone_numeros[7:]}'
        
        return telefone_formatado
    
    def clean_cep(self):
        """Valida e formata CEP"""
        cep = self.cleaned_data.get('cep', '')
        
        # Remove caracteres não numéricos
        cep_numeros = re.sub(r'[^0-9]', '', cep)
        
        # Verifica se tem exatamente 8 dígitos
        if len(cep_numeros) != 8:
            raise ValidationError('O CEP deve conter exatamente 8 dígitos.')
        
        # Formata: 00000-000
        cep_formatado = f'{cep_numeros[:5]}-{cep_numeros[5:]}'
        
        return cep_formatado
    
    def clean_data_nascimento(self):
        """Valida data de nascimento"""
        data_nasc = self.cleaned_data.get('data_nascimento')
        
        if not data_nasc:
            raise ValidationError('A data de nascimento é obrigatória.')
        
        # Data atual
        hoje = date.today()
        
        # Verifica se a data não é futura
        if data_nasc > hoje:
            raise ValidationError('A data de nascimento não pode ser uma data futura.')
        
        # Calcula idade
        idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
        
        # Verifica se tem pelo menos 1 ano (pode ajustar conforme necessário)
        if idade < 1:
            raise ValidationError('O paciente deve ter pelo menos 1 ano de idade.')
        
        # Verifica se não é muito antiga (ex: mais de 150 anos)
        if idade > 150:
            raise ValidationError('Data de nascimento inválida. Por favor, verifique.')
        
        return data_nasc


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
    
    def clean_arquivo(self):
        """Valida que o arquivo é um PDF"""
        arquivo = self.cleaned_data.get('arquivo')
        
        if arquivo:
            # Verifica extensão
            if not arquivo.name.lower().endswith('.pdf'):
                raise ValidationError('Apenas arquivos PDF são permitidos.')
            
            # Verifica tamanho (máximo 10MB)
            if arquivo.size > 10 * 1024 * 1024:
                raise ValidationError('O arquivo não pode ser maior que 10MB.')
        
        return arquivo


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
    
    def clean_imagem(self):
        """Valida que o arquivo é uma imagem"""
        imagem = self.cleaned_data.get('imagem')
        
        if imagem:
            # Verifica extensão
            extensoes_validas = ['.jpg', '.jpeg', '.png', '.gif']
            if not any(imagem.name.lower().endswith(ext) for ext in extensoes_validas):
                raise ValidationError('Apenas arquivos de imagem são permitidos (JPG, PNG, GIF).')
            
            # Verifica tamanho (máximo 5MB)
            if imagem.size > 5 * 1024 * 1024:
                raise ValidationError('A imagem não pode ser maior que 5MB.')
        
        return imagem