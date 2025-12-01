
# Файл конфигурации для сборщика документации Sphinx.
import os
import sys
# Указываем Sphinx, где искать исходный код (корневой каталог проекта)
sys.path.insert(0, os.path.abspath('..')) 


# -- Project information -----------------------------------------------------

project = 'My Python Project'
copyright = '2025, Developer'
author = 'Developer'

version = ''
release = ''


# -- General configuration ---------------------------------------------------

# Добавляем необходимые расширения
extensions = [
    'sphinx.ext.autodoc', # Основное для автодокументации
    'sphinx_rtd_theme', # Тема оформления Read The Docs
    'sphinx_autodoc_typehints' # Для обработки аннотаций типов
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Настройки Autodoc
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': False,
    'show-inheritance': True,
}
