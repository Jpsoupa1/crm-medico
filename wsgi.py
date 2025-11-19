"""
WSGI config for deployment.

This module contains the WSGI application used by Django's runserver
and is used by gunicorn for production deployment.
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório backend ao Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / 'backend'))

# Importa a aplicação WSGI do config
from config.wsgi import application

# Exporta a aplicação
__all__ = ['application']
