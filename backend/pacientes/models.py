# pacientes/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class Paciente(models.Model):
    """Modelo para armazenar informações dos pacientes"""
    
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]
    
    TIPO_SANGUE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    # Relação com o médico
    medico = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pacientes')
    
    # Informações básicas
    nome_completo = models.CharField(max_length=200)
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=14, unique=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    
    # Contato
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    
    # Endereço
    endereco = models.CharField(max_length=300)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=9)
    
    # Informações médicas
    tipo_sanguineo = models.CharField(max_length=3, choices=TIPO_SANGUE_CHOICES, blank=True)
    alergias = models.TextField(blank=True, help_text="Liste alergias conhecidas")
    medicamentos_uso = models.TextField(blank=True, help_text="Medicamentos em uso contínuo")
    historico_familiar = models.TextField(blank=True)
    observacoes = models.TextField(blank=True)
    
    # Controle
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['nome_completo']
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
    
    def __str__(self):
        return f"{self.nome_completo} - {self.cpf}"
    
    def get_idade(self):
        """Calcula a idade do paciente"""
        from datetime import date
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )


class Documento(models.Model):
    """Modelo para armazenar PDFs relacionados ao paciente"""
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='documentos')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    arquivo = models.FileField(
        upload_to='documentos/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    data_upload = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data_upload']
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
    
    def __str__(self):
        return f"{self.titulo} - {self.paciente.nome_completo}"


class Foto(models.Model):
    """Modelo para armazenar fotos relacionadas ao paciente"""
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='fotos')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    imagem = models.ImageField(
        upload_to='fotos/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])]
    )
    data_upload = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data_upload']
        verbose_name = 'Foto'
        verbose_name_plural = 'Fotos'
    
    def __str__(self):
        return f"{self.titulo} - {self.paciente.nome_completo}"