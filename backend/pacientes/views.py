# pacientes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Q, Value, F
from django.db.models.functions import Replace
from .models import Paciente, Documento, Foto
from .forms import PacienteForm, DocumentoForm, FotoForm


# ==================== AUTENTICAÇÃO ====================

def registro_view(request):
    """View para registro de novos médicos"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Erro ao criar conta. Verifique os dados.')
    else:
        form = UserCreationForm()
    
    return render(request, 'autenticacao/registro.html', {'form': form})


def login_view(request):
    """View para login de médicos"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo, {username}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'autenticacao/login.html', {'form': form})


def logout_view(request):
    """View para logout"""
    logout(request)
    messages.info(request, 'Você saiu do sistema.')
    return redirect('login')


# ==================== DASHBOARD ====================

@login_required
def dashboard_view(request):
    """Dashboard com lista de pacientes do médico"""
    busca = request.GET.get('busca', '')
    
    pacientes = Paciente.objects.filter(medico=request.user, ativo=True)
    
    if busca:
        # Remove caracteres não numéricos da busca para comparação limpa
        busca_limpa = ''.join(filter(str.isdigit, busca))
        
        filters = Q(nome_completo__icontains=busca)
        
        if busca_limpa:
            # Anota os campos limpos para comparação
            # CPF: remove . e -
            # Telefone: remove (, ), - e espaço
            pacientes = pacientes.annotate(
                cpf_limpo=Replace(
                    Replace(F('cpf'), Value('.'), Value('')), 
                    Value('-'), Value('')
                ),
                telefone_limpo=Replace(
                    Replace(
                        Replace(
                            Replace(F('telefone'), Value('('), Value('')), 
                            Value(')'), Value('')
                        ), 
                        Value('-'), Value('')
                    ), 
                    Value(' '), Value('')
                )
            )
            
            filters |= Q(cpf_limpo__icontains=busca_limpa)
            filters |= Q(telefone_limpo__icontains=busca_limpa)
        
        # Mantém a busca original também, para garantir
        filters |= Q(cpf__icontains=busca)
        filters |= Q(telefone__icontains=busca)
        
        pacientes = pacientes.filter(filters)
    
    pacientes = pacientes.order_by('-data_cadastro')
    
    context = {
        'pacientes': pacientes,
        'total_pacientes': Paciente.objects.filter(medico=request.user, ativo=True).count(),
        'busca': busca,
    }
    
    return render(request, 'pacientes/dashboard.html', context)


# ==================== CRUD PACIENTES ====================

@login_required
def paciente_criar_view(request):
    """View para criar novo paciente"""
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.medico = request.user
            paciente.save()
            messages.success(request, f'Paciente {paciente.nome_completo} cadastrado com sucesso!')
            return redirect('paciente_detalhes', pk=paciente.pk)
        else:
            messages.error(request, 'Erro ao cadastrar paciente. Verifique os dados.')
    else:
        form = PacienteForm()
    
    return render(request, 'pacientes/paciente_form.html', {'form': form, 'titulo': 'Cadastrar Novo Paciente'})


@login_required
def paciente_detalhes_view(request, pk):
    """View para visualizar detalhes do paciente"""
    paciente = get_object_or_404(Paciente, pk=pk, medico=request.user)
    documentos = paciente.documentos.all()
    fotos = paciente.fotos.all()
    
    context = {
        'paciente': paciente,
        'documentos': documentos,
        'fotos': fotos,
    }
    
    return render(request, 'pacientes/paciente_detalhes.html', context)


@login_required
def paciente_editar_view(request, pk):
    """View para editar paciente"""
    paciente = get_object_or_404(Paciente, pk=pk, medico=request.user)
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Dados de {paciente.nome_completo} atualizados com sucesso!')
            return redirect('paciente_detalhes', pk=paciente.pk)
        else:
            messages.error(request, 'Erro ao atualizar dados. Verifique os campos.')
    else:
        form = PacienteForm(instance=paciente)
    
    return render(request, 'pacientes/paciente_form.html', {
        'form': form,
        'titulo': f'Editar Paciente: {paciente.nome_completo}',
        'paciente': paciente
    })


@login_required
def paciente_deletar_view(request, pk):
    """View para deletar paciente"""
    paciente = get_object_or_404(Paciente, pk=pk, medico=request.user)
    
    if request.method == 'POST':
        nome = paciente.nome_completo
        paciente.delete()
        messages.success(request, f'Paciente {nome} removido com sucesso!')
        return redirect('dashboard')
    
    return render(request, 'pacientes/paciente_confirmar_delete.html', {'paciente': paciente})


# ==================== DOCUMENTOS ====================

@login_required
def documento_adicionar_view(request, paciente_pk):
    """View para adicionar documento ao paciente"""
    paciente = get_object_or_404(Paciente, pk=paciente_pk, medico=request.user)
    
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.paciente = paciente
            documento.save()
            messages.success(request, 'Documento adicionado com sucesso!')
            return redirect('paciente_detalhes', pk=paciente.pk)
        else:
            messages.error(request, 'Erro ao adicionar documento.')
    else:
        form = DocumentoForm()
    
    return render(request, 'pacientes/documento_form.html', {
        'form': form,
        'paciente': paciente
    })


@login_required
def documento_deletar_view(request, pk):
    """View para deletar documento"""
    documento = get_object_or_404(Documento, pk=pk, paciente__medico=request.user)
    paciente_pk = documento.paciente.pk
    
    if request.method == 'POST':
        documento.delete()
        messages.success(request, 'Documento removido com sucesso!')
        return redirect('paciente_detalhes', pk=paciente_pk)
    
    return render(request, 'pacientes/documento_confirmar_delete.html', {'documento': documento})


# ==================== FOTOS ====================

@login_required
def foto_adicionar_view(request, paciente_pk):
    """View para adicionar foto ao paciente"""
    paciente = get_object_or_404(Paciente, pk=paciente_pk, medico=request.user)
    
    if request.method == 'POST':
        form = FotoForm(request.POST, request.FILES)
        if form.is_valid():
            foto = form.save(commit=False)
            foto.paciente = paciente
            foto.save()
            messages.success(request, 'Foto adicionada com sucesso!')
            return redirect('paciente_detalhes', pk=paciente.pk)
        else:
            messages.error(request, 'Erro ao adicionar foto.')
    else:
        form = FotoForm()
    
    return render(request, 'pacientes/foto_form.html', {
        'form': form,
        'paciente': paciente
    })


@login_required
def foto_deletar_view(request, pk):
    """View para deletar foto"""
    foto = get_object_or_404(Foto, pk=pk, paciente__medico=request.user)
    paciente_pk = foto.paciente.pk
    
    if request.method == 'POST':
        foto.delete()
        messages.success(request, 'Foto removida com sucesso!')
        return redirect('paciente_detalhes', pk=paciente_pk)
    
    return render(request, 'pacientes/foto_confirmar_delete.html', {'foto': foto})