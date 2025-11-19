# pacientes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # CRUD Pacientes
    path('paciente/novo/', views.paciente_criar_view, name='paciente_criar'),
    path('paciente/<int:pk>/', views.paciente_detalhes_view, name='paciente_detalhes'),
    path('paciente/<int:pk>/editar/', views.paciente_editar_view, name='paciente_editar'),
    path('paciente/<int:pk>/deletar/', views.paciente_deletar_view, name='paciente_deletar'),
    
    # Documentos
    path('paciente/<int:paciente_pk>/documento/adicionar/', views.documento_adicionar_view, name='documento_adicionar'),
    path('documento/<int:pk>/deletar/', views.documento_deletar_view, name='documento_deletar'),
    
    # Fotos
    path('paciente/<int:paciente_pk>/foto/adicionar/', views.foto_adicionar_view, name='foto_adicionar'),
    path('foto/<int:pk>/deletar/', views.foto_deletar_view, name='foto_deletar'),
]