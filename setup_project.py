import json
import subprocess
from pathlib import Path
from typing import List

# ==============================================================================
# КОНСТАНТЫ НАСТРОЙКИ
# ==============================================================================

# 1. Настройки Ruff (для pyproject.toml)
RUFF_CONFIG = """
[tool.ruff]
# Длина строки (стандарт сейчас 88 или 100, 79 уже маловато)
line-length = 100
# Версия питона, под которую линтим
target-version = "py311"

[tool.ruff.lint]
# Какие правила включаем:
# E, W - стандартные ошибки (как в pycodestyle)
# F - pyflakes (баги, неиспользуемые переменные)
# I - isort (сортировка импортов - это киллер-фича!)
# B - flake8-bugbear (поиск неочевидных багов)
select = ["E", "W", "F", "I", "B"]
ignore = []

[tool.ruff.lint.isort]
# Группировать импорты правильно
known-first-party = ["app"]
"""
RUFF_PRE_COMMIT = """
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [ --fix ]
      - id: ruff-format
"""
PYTEST_CONFIG = """
[tool.pytest.ini_options]
# Указываем, что нужно добавить текущую директорию (корень проекта) в PYTHONPATH.
# Это позволяет импортировать пакеты из 'app'.
pythonpath = "." 
python_files = "test_*.py" # Указываем, какие файлы считать тестами
asyncio_mode = "auto"
"""
# 2. Настройки VS Code (для .vscode/settings.json)
VSCODE_SETTINGS = {
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": True,
        "editor.codeActionsOnSave": {
            "source.fixAll": "explicit",
            "source.organizeImports": "explicit",
        },
    }
}

# 3. Настройки .gitignore
GITIGNORE_CONTENT = """
# Python Environment and Artifacts
__pycache__/
*.py[cod]
.venv
.env
.pre-commit-config.yaml
# IDE and Build
.vscode/
dist/
*.egg-info/
.coverage
# Sphinx Documentation
docs/_build/
"""

# 4. Конфигурация Sphinx
SPHINX_CONF_PY_CONTENT = """
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
"""

SPHINX_INDEX_RST_CONTENT = """
.. Мой Python Проект документация

.. toctree::
   :maxdepth: 2
   :caption: Содержание:

   modules


.. Проект индексации
.. ====================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""

# Файл для включения автодокументации из исходного кода
SPHINX_MODULES_RST_CONTENT = """
Модули проекта
==============

.. automodule:: app
   :members:

.. automodule:: main
   :members:

.. Примечание: Если у вас другой основной файл/пакет (не 'app' или 'main'),
   измените эти директивы.
"""


# ==============================================================================
# ФУНКЦИИ ВЫПОЛНЕНИЯ КОМАНД И НАСТРОЙКИ ФАЙЛОВ
# ==============================================================================


def run_command(command: List[str]):
    """
    Выполняет команду в системе. Вывод стримится напрямую для повышения
    устойчивости к прерываниям в терминалах VS Code.
    """
    print(f"\n🚀 Выполнение: {' '.join(command)}")
    try:
        # check_call стримит вывод и поднимает ошибку, если код возврата не 0
        subprocess.check_call(command, shell=False)
        print("✅ Команда завершена успешно.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка выполнения команды: {e.cmd} (Код: {e.returncode})")
        exit(1)
    except FileNotFoundError:
        print(
            f"❌ Ошибка: Команда '{command[0]}' не найдена. Убедитесь, что она установлена и доступна в PATH."
        )
        exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Процесс был прерван. Пожалуйста, запустите скрипт заново.")
        exit(1)


def setup_poetry_and_ruff():
    """Шаг 0: Инициализация Poetry и установка Ruff/Sphinx."""
    print("--- 0. Инициализация Poetry и установка зависимостей ---")

    # 0.1 Poetry init: инициализация проекта с дефолтными настройками
    run_command(["poetry", "init", "-n"])
    print("✅ Poetry проект инициализирован.")

    # 0.2 Установка Ruff и Sphinx в качестве dev-зависимостей
    run_command(
        [
            "poetry",
            "add",
            "ruff",
            "sphinx",
            "sphinx-rtd-theme",
            "sphinx-autodoc-typehints",
            "pytest",
            "--group",
            "dev",
        ]
    )
    print("✅ Ruff и Sphinx установлены как инструменты разработки.")


def update_pyproject_toml(config_content: str):
    """Шаг 1: Добавление конфигурации Ruff в pyproject.toml."""
    print("\n--- 1. Настройка pyproject.toml (Ruff) ---")

    pyproject_path = Path("pyproject.toml")

    if pyproject_path.exists():
        try:
            with open(pyproject_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "[tool.ruff]" not in content:
                with open(pyproject_path, "a", encoding="utf-8") as f:
                    f.write("\n")
                    f.write(config_content.strip())
                print("✅ Секция [tool.ruff] добавлена в pyproject.toml.")
            else:
                print("ℹ️ Секция [tool.ruff] уже существует. Пропускаем запись.")

            if "[tool.pytest.ini_options]" not in content:
                with open(pyproject_path, "a", encoding="utf-8") as f:
                    f.write("\n")
                    f.write(config_content.strip())
                print("✅ Секция [tool.pytest.ini_options] добавлена в pyproject.toml.")
            else:
                print("ℹ️ Секция [tool.pytest.ini_options] уже существует. Пропускаем запись.")

        except IOError as e:
            print(f"❌ Не удалось прочитать/записать в pyproject.toml: {e}")
            exit(1)
    else:
        print("❌ Файл pyproject.toml не найден.")
        exit(1)


def create_vscode_settings(settings_data: dict):
    """Шаг 2: Создание .vscode/settings.json для авто-форматирования."""
    print("\n--- 2. Настройка VS Code (settings.json) ---")

    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    settings_path = vscode_dir / "settings.json"

    try:
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings_data, f, indent=4)

        print("✅ Файл .vscode/settings.json создан. Авто-форматирование Ruff включено.")
        print("   Не забудьте установить расширение 'Ruff' в VS Code!")
    except IOError as e:
        print(f"❌ Не удалось создать .vscode/settings.json: {e}")
        exit(1)


def create_git_files(gitignore_content: str):
    """Шаг 3: Создание .gitignore и .env."""
    print("\n--- 3. Настройка .gitignore и .env ---")

    # 3.1 Создание .gitignore
    gitignore_path = Path(".gitignore")
    try:
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write(gitignore_content.strip() + "\n")
        print("✅ Файл .gitignore создан.")
    except IOError as e:
        print(f"❌ Не удалось создать .gitignore: {e}")

    # 3.2 Создание пустого .env
    env_path = Path(".env")
    if not env_path.exists():
        env_path.touch()
        print("✅ Пустой файл .env создан.")
    else:
        print("ℹ️ Файл .env уже существует. Пропускаем создание.")


def create_ruff_pre_commit(ruff_content: str):
    """Шаг 3.3: Создание .pre-commit-config.yaml."""
    print("\n--- 3.1 .pre-commit-config.yaml---")

    gitignore_path = Path(".pre-commit-config.yaml")
    try:
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write(ruff_content.strip() + "\n")
        print("✅ Файл .pre-commit-config.yaml создан.")
    except IOError as e:
        print(f"❌ Не удалось создать .pre-commit-config.yaml: {e}")


def setup_sphinx_docs(conf_py_content: str, index_rst_content: str, modules_rst_content: str):
    """Шаг 4: Настройка Sphinx для автоматической документации."""
    print("\n--- 4. Настройка автоматической документации (Sphinx) ---")

    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)

    # 4.1 Создание вспомогательных папок
    Path(docs_dir / "_static").mkdir(exist_ok=True)
    Path(docs_dir / "_templates").mkdir(exist_ok=True)

    # 4.2 Создание conf.py
    try:
        with open(docs_dir / "conf.py", "w", encoding="utf-8") as f:
            f.write(conf_py_content)
        print("✅ docs/conf.py создан и настроен для Autodoc и Typehints.")
    except IOError as e:
        print(f"❌ Не удалось создать docs/conf.py: {e}")

    # 4.3 Создание index.rst
    try:
        with open(docs_dir / "index.rst", "w", encoding="utf-8") as f:
            f.write(index_rst_content)
        print("✅ docs/index.rst создан.")
    except IOError as e:
        print(f"❌ Не удалось создать docs/index.rst: {e}")

    # 4.4 Создание modules.rst для автодока
    try:
        with open(docs_dir / "modules.rst", "w", encoding="utf-8") as f:
            f.write(modules_rst_content)
        print("✅ docs/modules.rst создан для автодокументации модулей.")
    except IOError as e:
        print(f"❌ Не удалось создать docs/modules.rst: {e}")

    print(
        "\n✨ Документация готова к сборке. Запустите 'poetry run sphinx-build -b html docs _build' для генерации HTML."
    )


def main():
    """Основная функция настройки проекта."""
    print("======================================================")
    print("=== ЗАПУСК АВТОМАТИЧЕСКОЙ НАСТРОЙКИ ПРОЕКТА PYTHON ===")
    print("======================================================")

    # 0. Инициализация Poetry и установка зависимостей
    setup_poetry_and_ruff()

    # 1. Настройка Ruff в pyproject.toml
    update_pyproject_toml(RUFF_CONFIG)
    # 2 установка pytest
    update_pyproject_toml(PYTEST_CONFIG)
    Path("tests").mkdir(exist_ok=True)

    # 2. Настройка VS Code
    create_vscode_settings(VSCODE_SETTINGS)

    # 3. Создание .gitignore и .env
    create_git_files(GITIGNORE_CONTENT)

    create_ruff_pre_commit(RUFF_PRE_COMMIT)

    # 4. Настройка Sphinx
    setup_sphinx_docs(SPHINX_CONF_PY_CONTENT, SPHINX_INDEX_RST_CONTENT, SPHINX_MODULES_RST_CONTENT)
    # 5. добавление линтера (если проект совершенно новый)
    # run_command("poetry", "add", "pylint")

    print("\n======================================================")
    print("=== НАСТРОЙКА ЗАВЕРШЕНА УСПЕШНО! ===")
    print("1. Выполните 'poetry install'.")
    print("2. Перезагрузите VS Code, чтобы активировать настройки Ruff.")
    print("3. Напишите docstrings в коде и соберите документацию:")
    print("   poetry run sphinx-build -b html docs _build")
    print("=======================================================")
    print("Для диаграммы классов и компонентов выполни следующие команды")
    print("Раскидай по модулями приложения __init__.py")
    print("  poetry add pylint")
    print("  poetry run pyreverse -o png -p Octamillia -A -S app/")
    print("=======================================================")
    print("""Параметр	Описание
-o png	Указывает формат выходного файла (PNG, SVG, или DOT).
-p Octamillia	Указывает имя пакета (название диаграммы).
-A	Включает все классы, включая абстрактные (TentacleContract(ABC)).
-S	Критически важно: Убирает стандартные классы Python (например, object, dict, BaseModel), делая диаграмму чище.
app/	Указывает директорию, которую нужно сканировать.""")


if __name__ == "__main__":
    main()
