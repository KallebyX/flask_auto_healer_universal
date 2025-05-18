#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de relatório JSON para o Agente Flask Autocurador Supremo Universal.

Este módulo contém a classe para geração de relatórios em formato JSON.
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from ..core.detector import FlaskProjectDetector
from ..core.diagnostic import DiagnosticEngine


class JSONReporter:
    """
    Gerador de relatórios JSON para o Agente Flask Autocurador Supremo Universal.
    """
    
    def __init__(self, detector: FlaskProjectDetector, diagnostic: DiagnosticEngine):
        """
        Inicializa o gerador de relatórios JSON.
        
        Args:
            detector: Detector de estrutura de projetos Flask.
            diagnostic: Motor de diagnóstico com problemas identificados.
        """
        self.detector = detector
        self.diagnostic = diagnostic
        self.healing = None
        self.structure = detector.detected_structure
        self.issues = diagnostic.issues
    
    def set_healing_engine(self, healing) -> None:
        """
        Define o motor de correção.
        
        Args:
            healing: Motor de correção com correções aplicadas.
        """
        self.healing = healing
        self.fixes = healing.fixes
    
    def generate(self, output_path: Union[str, Path]) -> None:
        """
        Gera o relatório JSON.
        
        Args:
            output_path: Caminho para o arquivo de saída.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Gera o conteúdo JSON
        json_content = self._generate_json_content()
        
        # Salva o arquivo
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_content, f, indent=2)
    
    def _generate_json_content(self) -> Dict[str, Any]:
        """
        Gera o conteúdo JSON do relatório.
        
        Returns:
            Conteúdo JSON do relatório.
        """
        # Obtém os dados para o relatório
        project_name = Path(self.structure['project_path']).name
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Conta os problemas e correções
        total_issues = sum(len(self.issues[category]) for category in self.issues)
        total_fixes = 0
        if self.healing:
            total_fixes = sum(len(self.fixes[category]) for category in self.fixes)
        
        # Conta problemas por severidade
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        for category in self.issues:
            for issue in self.issues[category]:
                severity = issue.get("severity", "medium")
                severity_counts[severity] += 1
        
        # Prepara os dados do relatório
        report_data = {
            "meta": {
                "project_name": project_name,
                "project_path": str(self.structure['project_path']),
                "timestamp": timestamp,
                "version": "1.0.0"
            },
            "summary": {
                "total_issues": total_issues,
                "total_fixes": total_fixes,
                "severity_counts": severity_counts,
                "pattern": self.structure['pattern'],
                "database_type": self.structure['database']['type'],
                "auth_type": self.structure['auth']['type']
            },
            "structure": {
                "pattern": self.structure['pattern'],
                "database": self.structure['database'],
                "auth": self.structure['auth'],
                "app_files_count": len(self.structure['app_files']),
                "blueprint_files_count": len(self.structure['blueprint_files']),
                "template_dirs_count": len(self.structure['template_dirs']),
                "static_dirs_count": len(self.structure['static_dirs']),
                "model_files_count": len(self.structure['model_files']),
                "route_files_count": len(self.structure['route_files']),
                "config_files_count": len(self.structure['config_files'])
            },
            "components": {
                "templates": [
                    {
                        "name": template["name"],
                        "relative_path": template["relative_path"]
                    }
                    for template in self.detector.get_templates()
                ],
                "routes": [
                    {
                        "path": route["path"],
                        "function": route["function"],
                        "methods": route["methods"],
                        "app_or_blueprint": route["app_or_blueprint"]
                    }
                    for route in self.detector.get_routes()
                ],
                "models": [
                    {
                        "name": model["name"],
                        "fields": model["fields"]
                    }
                    for model in self.detector.get_models()
                ],
                "blueprints": self.detector.get_blueprints()
            },
            "issues": self.issues
        }
        
        # Adiciona informações de correção se disponíveis
        if self.healing:
            report_data["fixes"] = self.fixes
        
        return report_data
