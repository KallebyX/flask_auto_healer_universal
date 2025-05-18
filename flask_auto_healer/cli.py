#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI universal para o Agente Flask Autocurador Supremo.

Este módulo implementa a interface de linha de comando universal
para o Agente Flask Autocurador Supremo, com suporte a presets
e opções modulares.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from .core.detector import FlaskProjectDetector
from .core.diagnostic import DiagnosticEngine
from .core.healing import HealingEngine
from .reporters.html_reporter import HTMLReporter
from .reporters.json_reporter import JSONReporter
from .reporters.markdown_reporter import MarkdownReporter
from .presets.manager import PresetManager


class FlaskAutoHealerCLI:
    """
    Interface de linha de comando universal para o Agente Flask Autocurador Supremo.
    """
    
    def __init__(self):
        """
        Inicializa a CLI.
        """
        self.parser = self._create_parser()
        self.args = None
        self.project_path = None
        self.detector = None
        self.diagnostic = None
        self.healing = None
        self.preset_manager = None
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """
        Configura o logger.
        
        Returns:
            Logger configurado.
        """
        logger = logging.getLogger('flask_auto_healer')
        logger.setLevel(logging.INFO)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
        return logger
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """
        Cria o parser de argumentos.
        
        Returns:
            Parser de argumentos.
        """
        parser = argparse.ArgumentParser(
            description='Agente Flask Autocurador Supremo Universal',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Exemplos de uso:
  flask-auto-healer run                      # Executa diagnóstico e correção com detecção automática
  flask-auto-healer run --somente-testar     # Executa apenas diagnóstico sem correções
  flask-auto-healer run --preset=blog        # Usa preset específico para blogs
  flask-auto-healer report --format=html     # Gera relatório HTML do último diagnóstico
  flask-auto-healer generate github-workflow # Gera template para GitHub Actions
"""
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
        
        # Comando run
        run_parser = subparsers.add_parser('run', help='Executa diagnóstico e correção')
        run_parser.add_argument('--project-path', type=str, default='.', help='Caminho do projeto Flask (padrão: diretório atual)')
        run_parser.add_argument('--corrigir-tudo', action='store_true', help='Corrige todos os problemas encontrados')
        run_parser.add_argument('--somente-testar', action='store_true', help='Apenas testa sem fazer correções')
        run_parser.add_argument('--modo-silencioso', action='store_true', help='Executa em modo silencioso')
        run_parser.add_argument('--auto-detect', action='store_true', help='Força detecção automática da estrutura')
        run_parser.add_argument('--blueprint-aware', action='store_true', help='Modo consciente de blueprints')
        run_parser.add_argument('--no-db', action='store_true', help='Ignora verificações de banco de dados')
        run_parser.add_argument('--force', action='store_true', help='Força correções mesmo em casos duvidosos')
        run_parser.add_argument('--profile', action='store_true', help='Executa com profiling de performance')
        run_parser.add_argument('--preset', type=str, choices=['blog', 'ecommerce', 'admin-panel'], help='Usa preset específico')
        run_parser.add_argument('--watch', action='store_true', help='Modo watcher para correções em tempo real')
        run_parser.add_argument('--simulate-prod', action='store_true', help='Simula ambiente de produção')
        run_parser.add_argument('--usar-ai', action='store_true', help='Usa IA para sugestões avançadas')
        run_parser.add_argument('--debug', action='store_true', help='Modo debug com informações detalhadas')
        run_parser.add_argument('--relatorio-html', action='store_true', help='Gera relatório HTML')
        run_parser.add_argument('--relatorio-json', action='store_true', help='Gera relatório JSON')
        run_parser.add_argument('--relatorio-md', action='store_true', help='Gera relatório Markdown')
        
        # Comando report
        report_parser = subparsers.add_parser('report', help='Gera relatórios')
        report_parser.add_argument('--format', type=str, default='html', help='Formato do relatório (html, json, md, all)')
        report_parser.add_argument('--output-dir', type=str, default='./reports', help='Diretório de saída para relatórios')
        report_parser.add_argument('--bundle', action='store_true', help='Gera diagnostic_bundle.zip com todos os relatórios')
        
        # Comando generate
        generate_parser = subparsers.add_parser('generate', help='Gera templates e arquivos de configuração')
        generate_parser.add_argument('template', choices=['github-workflow', 'gitlab-ci', 'docker', 'config'], help='Template a ser gerado')
        generate_parser.add_argument('--output-dir', type=str, default='.', help='Diretório de saída para templates')
        
        # Comando version
        subparsers.add_parser('version', help='Mostra a versão do Agente Flask Autocurador Supremo')
        
        return parser
    
    def parse_args(self, args=None) -> None:
        """
        Processa os argumentos da linha de comando.
        
        Args:
            args: Argumentos da linha de comando. Se None, usa sys.argv.
        """
        self.args = self.parser.parse_args(args)
        
        # Configura o logger com base nos argumentos
        if hasattr(self.args, 'debug') and self.args.debug:
            self.logger.setLevel(logging.DEBUG)
            for handler in self.logger.handlers:
                handler.setLevel(logging.DEBUG)
        
        if hasattr(self.args, 'modo_silencioso') and self.args.modo_silencioso:
            self.logger.setLevel(logging.WARNING)
            for handler in self.logger.handlers:
                handler.setLevel(logging.WARNING)
    
    def run(self) -> int:
        """
        Executa o comando especificado.
        
        Returns:
            Código de saída (0 para sucesso, diferente de 0 para erro).
        """
        if not self.args:
            self.parse_args()
        
        try:
            if self.args.command == 'run':
                return self._run_command()
            elif self.args.command == 'report':
                return self._report_command()
            elif self.args.command == 'generate':
                return self._generate_command()
            elif self.args.command == 'version':
                return self._version_command()
            else:
                self.parser.print_help()
                return 0
        except Exception as e:
            self.logger.error(f"Erro ao executar comando: {str(e)}")
            if hasattr(self.args, 'debug') and self.args.debug:
                import traceback
                self.logger.error(traceback.format_exc())
            return 1
    
    def _run_command(self) -> int:
        """
        Executa o comando run.
        
        Returns:
            Código de saída (0 para sucesso, diferente de 0 para erro).
        """
        self.project_path = Path(self.args.project_path).resolve()
        self.logger.info(f"Analisando projeto em: {self.project_path}")
        
        # Inicializa o detector
        self.detector = FlaskProjectDetector(self.project_path)
        
        # Detecta a estrutura do projeto
        structure = self.detector.detect()
        self.logger.info(f"Estrutura detectada: {structure['pattern']}")
        
        # Inicializa o preset manager se necessário
        if self.args.preset:
            self.preset_manager = PresetManager(self.detector)
            self.preset_manager.load_preset(self.args.preset)
            self.logger.info(f"Preset carregado: {self.args.preset}")
        
        # Executa o diagnóstico
        self.diagnostic = DiagnosticEngine(self.detector)
        issues = self.diagnostic.diagnose()
        
        # Conta os problemas
        total_issues = sum(len(issues[category]) for category in issues)
        self.logger.info(f"Total de problemas encontrados: {total_issues}")
        
        # Mostra resumo dos problemas
        for category in issues:
            if issues[category]:
                self.logger.info(f"Problemas em {category}: {len(issues[category])}")
        
        # Executa a correção se necessário
        if not self.args.somente_testar and (self.args.corrigir_tudo or total_issues > 0):
            self.healing = HealingEngine(self.detector, self.diagnostic)
            fixes = self.healing.heal()
            
            # Conta as correções
            total_fixes = sum(len(fixes[category]) for category in fixes)
            self.logger.info(f"Total de correções aplicadas: {total_fixes}")
            
            # Mostra resumo das correções
            for category in fixes:
                if fixes[category]:
                    self.logger.info(f"Correções em {category}: {len(fixes[category])}")
        
        # Gera relatórios se solicitado
        if self.args.relatorio_html:
            self._generate_html_report()
        
        if self.args.relatorio_json:
            self._generate_json_report()
        
        if self.args.relatorio_md:
            self._generate_markdown_report()
        
        return 0
    
    def _report_command(self) -> int:
        """
        Executa o comando report.
        
        Returns:
            Código de saída (0 para sucesso, diferente de 0 para erro).
        """
        output_dir = Path(self.args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Verifica se há dados de diagnóstico
        if not hasattr(self, 'diagnostic') or not self.diagnostic:
            self.logger.error("Nenhum diagnóstico encontrado. Execute 'run' primeiro.")
            return 1
        
        formats = self.args.format.split(',')
        
        if 'all' in formats:
            formats = ['html', 'json', 'md']
        
        for fmt in formats:
            if fmt == 'html':
                self._generate_html_report(output_dir)
            elif fmt == 'json':
                self._generate_json_report(output_dir)
            elif fmt == 'md':
                self._generate_markdown_report(output_dir)
        
        # Gera bundle se solicitado
        if self.args.bundle:
            self._generate_diagnostic_bundle(output_dir)
        
        return 0
    
    def _generate_command(self) -> int:
        """
        Executa o comando generate.
        
        Returns:
            Código de saída (0 para sucesso, diferente de 0 para erro).
        """
        output_dir = Path(self.args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.args.template == 'github-workflow':
            self._generate_github_workflow(output_dir)
        elif self.args.template == 'gitlab-ci':
            self._generate_gitlab_ci(output_dir)
        elif self.args.template == 'docker':
            self._generate_docker(output_dir)
        elif self.args.template == 'config':
            self._generate_config(output_dir)
        
        return 0
    
    def _version_command(self) -> int:
        """
        Executa o comando version.
        
        Returns:
            Código de saída (0 para sucesso, diferente de 0 para erro).
        """
        from . import __version__
        print(f"Agente Flask Autocurador Supremo Universal v{__version__}")
        return 0
    
    def _generate_html_report(self, output_dir: Optional[Path] = None) -> None:
        """
        Gera relatório HTML.
        
        Args:
            output_dir: Diretório de saída para o relatório.
        """
        if output_dir is None:
            output_dir = Path('./reports')
            output_dir.mkdir(parents=True, exist_ok=True)
        
        reporter = HTMLReporter(self.detector, self.diagnostic)
        if hasattr(self, 'healing') and self.healing:
            reporter.set_healing_engine(self.healing)
        
        report_path = output_dir / 'report.html'
        reporter.generate(report_path)
        self.logger.info(f"Relatório HTML gerado: {report_path}")
    
    def _generate_json_report(self, output_dir: Optional[Path] = None) -> None:
        """
        Gera relatório JSON.
        
        Args:
            output_dir: Diretório de saída para o relatório.
        """
        if output_dir is None:
            output_dir = Path('./reports')
            output_dir.mkdir(parents=True, exist_ok=True)
        
        reporter = JSONReporter(self.detector, self.diagnostic)
        if hasattr(self, 'healing') and self.healing:
            reporter.set_healing_engine(self.healing)
        
        report_path = output_dir / 'report.json'
        reporter.generate(report_path)
        self.logger.info(f"Relatório JSON gerado: {report_path}")
    
    def _generate_markdown_report(self, output_dir: Optional[Path] = None) -> None:
        """
        Gera relatório Markdown.
        
        Args:
            output_dir: Diretório de saída para o relatório.
        """
        if output_dir is None:
            output_dir = Path('./reports')
            output_dir.mkdir(parents=True, exist_ok=True)
        
        reporter = MarkdownReporter(self.detector, self.diagnostic)
        if hasattr(self, 'healing') and self.healing:
            reporter.set_healing_engine(self.healing)
        
        report_path = output_dir / 'report.md'
        reporter.generate(report_path)
        self.logger.info(f"Relatório Markdown gerado: {report_path}")
    
    def _generate_diagnostic_bundle(self, output_dir: Path) -> None:
        """
        Gera bundle de diagnóstico.
        
        Args:
            output_dir: Diretório de saída para o bundle.
        """
        import zipfile
        import datetime
        
        # Gera todos os relatórios
        self._generate_html_report(output_dir)
        self._generate_json_report(output_dir)
        self._generate_markdown_report(output_dir)
        
        # Cria o bundle
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        bundle_path = output_dir / f'diagnostic_bundle_{timestamp}.zip'
        
        with zipfile.ZipFile(bundle_path, 'w') as zipf:
            for report_file in ['report.html', 'report.json', 'report.md']:
                report_path = output_dir / report_file
                if report_path.exists():
                    zipf.write(report_path, report_file)
        
        self.logger.info(f"Bundle de diagnóstico gerado: {bundle_path}")
    
    def _generate_github_workflow(self, output_dir: Path) -> None:
        """
        Gera template para GitHub Actions.
        
        Args:
            output_dir: Diretório de saída para o template.
        """
        workflow_dir = output_dir / '.github' / 'workflows'
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_path = workflow_dir / 'autoheal.yml'
        
        workflow_content = """name: Flask Auto Healer

on:
  pull_request:
    branches: [ main, master, develop ]
  workflow_dispatch:

jobs:
  auto-heal:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flask-auto-healer
    
    - name: Run Flask Auto Healer
      run: |
        flask-auto-healer run --somente-testar --relatorio-md
    
    - name: Upload diagnostic report
      uses: actions/upload-artifact@v3
      with:
        name: flask-auto-healer-report
        path: reports/
"""
        
        with open(workflow_path, 'w', encoding='utf-8') as f:
            f.write(workflow_content)
        
        self.logger.info(f"Template para GitHub Actions gerado: {workflow_path}")
    
    def _generate_gitlab_ci(self, output_dir: Path) -> None:
        """
        Gera template para GitLab CI/CD.
        
        Args:
            output_dir: Diretório de saída para o template.
        """
        gitlab_ci_path = output_dir / '.gitlab-ci.yml'
        
        gitlab_ci_content = """stages:
  - test

flask-auto-healer:
  stage: test
  image: python:3.9
  script:
    - pip install flask-auto-healer
    - flask-auto-healer run --somente-testar --relatorio-md
  artifacts:
    paths:
      - reports/
    expire_in: 1 week
"""
        
        with open(gitlab_ci_path, 'w', encoding='utf-8') as f:
            f.write(gitlab_ci_content)
        
        self.logger.info(f"Template para GitLab CI/CD gerado: {gitlab_ci_path}")
    
    def _generate_docker(self, output_dir: Path) -> None:
        """
        Gera template para Docker.
        
        Args:
            output_dir: Diretório de saída para o template.
        """
        dockerfile_path = output_dir / 'Dockerfile'
        
        dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir flask-auto-healer

CMD ["flask-auto-healer", "run", "--corrigir-tudo", "--relatorio-html"]
"""
        
        with open(dockerfile_path, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        
        self.logger.info(f"Template para Docker gerado: {dockerfile_path}")
    
    def _generate_config(self, output_dir: Path) -> None:
        """
        Gera arquivo de configuração.
        
        Args:
            output_dir: Diretório de saída para o arquivo de configuração.
        """
        config_path = output_dir / '.flask-auto-healer.json'
        
        config_content = {
            "project_path": ".",
            "auto_detect": True,
            "blueprint_aware": True,
            "no_db": False,
            "force": False,
            "profile": False,
            "preset": None,
            "watch": False,
            "simulate_prod": False,
            "usar_ai": False,
            "debug": False,
            "reports": {
                "html": True,
                "json": True,
                "md": True,
                "output_dir": "./reports"
            },
            "ignore_patterns": [
                "venv/",
                "env/",
                "__pycache__/",
                "*.pyc",
                "migrations/"
            ]
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_content, f, indent=2)
        
        self.logger.info(f"Arquivo de configuração gerado: {config_path}")


def main():
    """
    Função principal para execução via linha de comando.
    """
    cli = FlaskAutoHealerCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
