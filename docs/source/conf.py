import os
import sys

# Вказуємо шлях до кореня проекту
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------
project = 'Contacts App'
copyright = '2026, Vlad Popov'
author = 'Vlad Popov'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# Додаємо розширення ТІЛЬКИ ТУТ (один раз)
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# Виберіть одну тему
html_theme = 'nature' 
html_static_path = ['_static']