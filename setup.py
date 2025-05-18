#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flask-auto-healer",
    version="1.0.0",
    author="Manus AI",
    author_email="contato@manus.ai",
    description="Agente Flask Autocurador Supremo Universal - Ferramenta de diagnóstico e correção automática para projetos Flask",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/manus-ai/flask-auto-healer",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.9",
    install_requires=[
        "flask>=2.0.0",
        "flask-login>=0.6.0",
        "flask-sqlalchemy>=3.0.0",
        "rich>=10.0.0",
        "faker>=8.0.0",
        "beautifulsoup4>=4.9.0",
        "isort>=5.0.0",
        "black>=21.0.0",
        "flake8>=4.0.0",
        "pylint>=2.0.0",
        "typer>=0.7.0",
        "jinja2>=3.0.0",
        "pyyaml>=5.4.0",
    ],
    extras_require={
        "ai": ["openai>=0.27.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "tox>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "flask-auto-healer=flask_auto_healer.cli:main",
        ],
    },
)
