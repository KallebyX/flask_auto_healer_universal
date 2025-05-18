#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo principal do Agente Flask Autocurador Supremo Universal.

Este módulo fornece a API principal para uso do Agente Flask Autocurador
como uma biblioteca em outros projetos.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from .core.detector import FlaskProjectDetector
from .core.diagnostic import DiagnosticEngine
from .core.healing import HealingEngine
from .reporters.html_reporter import HTMLReporter
from .reporters.json_reporter import JSONReporter
from .reporters.markdown_reporter import MarkdownReporter
from .presets.manager import PresetManager

__version__ = '1.0.0'


class FlaskAutoHealer:
    """
    API principal do Agente Flask Autocurador Supremo Universal.
    
    Esta classe fornece uma interface programática para uso do Agente
    como uma biblioteca em outros projetos.
    """
    
    def __init__(self, project_path: Union[str, Path] = '.', preset: Optional[str] = None, debug: bool = False):
        """
        Inicializa o Agente Flask Autocurador.
        
        Args:
            project_path: Caminho para o diretório raiz do projeto Flask.
            preset: Preset a ser utilizado (blog, ecommerce, admin-panel).
            debug: Se True, ativa o modo debug com logs detalhados.
        """
        self.project_path = Path(project_path).resolve()
        self.preset_name = preset
        self.debug = debug
        
        self.detector = None
        self.diagnostic = None
        self.healing = None
        self.preset_manager = None
        
        self.structure = None
        self.issues = None
        self.fixes = None
        
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """
        Configura o logger.
        
        Returns:
            Logger configurado.
        """
        logger = logging.getLogger('flask_auto_healer')
        
        # Limpa handlers existentes
        if logger.handlers:
            logger.handlers = []
        
        logger.setLevel(logging.INFO if not self.debug else logging.DEBUG)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO if not self.debug else logging.DEBUG)
        
        # Formato
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
        return logger
    
    def detect(self) -> Dict[str, Any]:
        """
        Detecta a estrutura do projeto Flask.
        
        Returns:
            Dict contendo a estrutura detectada do projeto.
        """
        self.logger.info(f"Detectando estrutura do projeto em: {self.project_path}")
        
        self.detector = FlaskProjectDetector(self.project_path)
        self.structure = self.detector.detect()
        
        self.logger.info(f"Estrutura detectada: {self.structure['pattern']}")
        
        # Inicializa o preset manager se necessário
        if self.preset_name:
            self.preset_manager = PresetManager(self.detector)
            self.preset_manager.load_preset(self.preset_name)
            self.logger.info(f"Preset carregado: {self.preset_name}")
        
        return self.structure
    
    def diagnose(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Diagnostica problemas no projeto Flask.
        
        Returns:
            Dict contendo os problemas encontrados.
        """
        if not self.detector:
            self.detect()
        
        self.logger.info("Diagnosticando problemas no projeto...")
        
        self.diagnostic = DiagnosticEngine(self.detector)
        self.issues = self.diagnostic.diagnose()
        
        # Conta os problemas
        total_issues = sum(len(self.issues[category]) for category in self.issues)
        self.logger.info(f"Total de problemas encontrados: {total_issues}")
        
        # Mostra resumo dos problemas
        for category in self.issues:
            if self.issues[category]:
                self.logger.info(f"Problemas em {category}: {len(self.issues[category])}")
        
        return self.issues
    
    def heal(self, create_backups: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        Corrige problemas no projeto Flask.
        
        Args:
            create_backups: Se True, cria backups dos arquivos antes de modificá-los.
            
        Returns:
            Dict contendo as correções aplicadas.
        """
        if not self.diagnostic:
            self.diagnose()
        
        self.logger.info("Corrigindo problemas no projeto...")
        
        self.healing = HealingEngine(self.detector, self.diagnostic)
        self.fixes = self.healing.heal(create_backups=create_backups)
        
        # Conta as correções
        total_fixes = sum(len(self.fixes[category]) for category in self.fixes)
        self.logger.info(f"Total de correções aplicadas: {total_fixes}")
        
        # Mostra resumo das correções
        for category in self.fixes:
            if self.fixes[category]:
                self.logger.info(f"Correções em {category}: {len(self.fixes[category])}")
        
        return self.fixes
    
    def generate_report(self, format: str = 'html', output_dir: Union[str, Path] = './reports') -> Path:
        """
        Gera relatório do diagnóstico e correções.
        
        Args:
            format: Formato do relatório (html, json, md).
            output_dir: Diretório de saída para o relatório.
            
        Returns:
            Caminho para o relatório gerado.
        """
        if not self.diagnostic:
            self.diagnose()
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = None
        
        if format == 'html':
            reporter = HTMLReporter(self.detector, self.diagnostic)
            if self.healing:
                reporter.set_healing_engine(self.healing)
            
            report_path = output_dir / 'report.html'
            reporter.generate(report_path)
            self.logger.info(f"Relatório HTML gerado: {report_path}")
        
        elif format == 'json':
            reporter = JSONReporter(self.detector, self.diagnostic)
            if self.healing:
                reporter.set_healing_engine(self.healing)
            
            report_path = output_dir / 'report.json'
            reporter.generate(report_path)
            self.logger.info(f"Relatório JSON gerado: {report_path}")
        
        elif format == 'md':
            reporter = MarkdownReporter(self.detector, self.diagnostic)
            if self.healing:
                reporter.set_healing_engine(self.healing)
            
            report_path = output_dir / 'report.md'
            reporter.generate(report_path)
            self.logger.info(f"Relatório Markdown gerado: {report_path}")
        
        else:
            self.logger.error(f"Formato de relatório não suportado: {format}")
            return None
        
        return report_path
    
    def generate_diagnostic_bundle(self, output_dir: Union[str, Path] = './reports') -> Path:
        """
        Gera bundle de diagnóstico com todos os relatórios.
        
        Args:
            output_dir: Diretório de saída para o bundle.
            
        Returns:
            Caminho para o bundle gerado.
        """
        import zipfile
        import datetime
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Gera todos os relatórios
        self.generate_report('html', output_dir)
        self.generate_report('json', output_dir)
        self.generate_report('md', output_dir)
        
        # Cria o bundle
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        bundle_path = output_dir / f'diagnostic_bundle_{timestamp}.zip'
        
        with zipfile.ZipFile(bundle_path, 'w') as zipf:
            for report_file in ['report.html', 'report.json', 'report.md']:
                report_path = output_dir / report_file
                if report_path.exists():
                    zipf.write(report_path, report_file)
        
        self.logger.info(f"Bundle de diagnóstico gerado: {bundle_path}")
        
        return bundle_path
    
    def get_detector(self) -> FlaskProjectDetector:
        """
        Retorna o detector de estrutura.
        
        Returns:
            Detector de estrutura.
        """
        if not self.detector:
            self.detect()
        
        return self.detector
    
    def get_diagnostic_engine(self) -> DiagnosticEngine:
        """
        Retorna o motor de diagnóstico.
        
        Returns:
            Motor de diagnóstico.
        """
        if not self.diagnostic:
            self.diagnose()
        
        return self.diagnostic
    
    def get_healing_engine(self) -> Optional[HealingEngine]:
        """
        Retorna o motor de correção.
        
        Returns:
            Motor de correção ou None se não inicializado.
        """
        return self.healing
    
    def get_preset_manager(self) -> Optional[PresetManager]:
        """
        Retorna o gerenciador de presets.
        
        Returns:
            Gerenciador de presets ou None se não inicializado.
        """
        return self.preset_manager
    
    def run_full_cycle(self, create_backups: bool = True, generate_reports: bool = True) -> Dict[str, Any]:
        """
        Executa o ciclo completo de detecção, diagnóstico e correção.
        
        Args:
            create_backups: Se True, cria backups dos arquivos antes de modificá-los.
            generate_reports: Se True, gera relatórios em todos os formatos.
            
        Returns:
            Dict contendo resultados do ciclo completo.
        """
        self.detect()
        self.diagnose()
        self.heal(create_backups=create_backups)
        
        if generate_reports:
            reports = {
                'html': self.generate_report('html'),
                'json': self.generate_report('json'),
                'md': self.generate_report('md'),
                'bundle': self.generate_diagnostic_bundle()
            }
        else:
            reports = None
        
        return {
            'structure': self.structure,
            'issues': self.issues,
            'fixes': self.fixes,
            'reports': reports
        }


# Função auxiliar para uso rápido
def auto_heal_flask_project(project_path: Union[str, Path] = '.', preset: Optional[str] = None, 
                           create_backups: bool = True, generate_reports: bool = True) -> Dict[str, Any]:
    """
    Executa o ciclo completo de detecção, diagnóstico e correção em um projeto Flask.
    
    Args:
        project_path: Caminho para o diretório raiz do projeto Flask.
        preset: Preset a ser utilizado (blog, ecommerce, admin-panel).
        create_backups: Se True, cria backups dos arquivos antes de modificá-los.
        generate_reports: Se True, gera relatórios em todos os formatos.
        
    Returns:
        Dict contendo resultados do ciclo completo.
    """
    healer = FlaskAutoHealer(project_path, preset)
    return healer.run_full_cycle(create_backups=create_backups, generate_reports=generate_reports)
