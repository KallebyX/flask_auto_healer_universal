#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de relatório HTML para o Agente Flask Autocurador Supremo Universal.

Este módulo contém a classe para geração de relatórios em formato HTML.
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from ..core.detector import FlaskProjectDetector
from ..core.diagnostic import DiagnosticEngine


class HTMLReporter:
    """
    Gerador de relatórios HTML para o Agente Flask Autocurador Supremo Universal.
    """
    
    def __init__(self, detector: FlaskProjectDetector, diagnostic: DiagnosticEngine):
        """
        Inicializa o gerador de relatórios HTML.
        
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
        Gera o relatório HTML.
        
        Args:
            output_path: Caminho para o arquivo de saída.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Gera o conteúdo HTML
        html_content = self._generate_html_content()
        
        # Salva o arquivo
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_html_content(self) -> str:
        """
        Gera o conteúdo HTML do relatório.
        
        Returns:
            Conteúdo HTML do relatório.
        """
        # Obtém os dados para o relatório
        project_name = Path(self.structure['project_path']).name
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Conta os problemas e correções
        total_issues = sum(len(self.issues[category]) for category in self.issues)
        total_fixes = 0
        if self.healing:
            total_fixes = sum(len(self.fixes[category]) for category in self.fixes)
        
        # Gera o HTML
        html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório do Agente Flask Autocurador - {project_name}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.3/font/bootstrap-icons.css">
    <style>
        :root {{
            --primary-color: #007bff;
            --secondary-color: #6c757d;
            --success-color: #28a745;
            --danger-color: #dc3545;
            --warning-color: #ffc107;
            --info-color: #17a2b8;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        .header {{
            background: linear-gradient(135deg, var(--primary-color), #0056b3);
            color: white;
            padding: 2rem 0;
            border-radius: 0 0 10px 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .card {{
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin-bottom: 1.5rem;
            border: none;
        }}
        .card-header {{
            border-radius: 10px 10px 0 0 !important;
            font-weight: 600;
        }}
        .severity-high {{
            color: var(--danger-color);
        }}
        .severity-medium {{
            color: var(--warning-color);
        }}
        .severity-low {{
            color: var(--info-color);
        }}
        .status-card {{
            text-align: center;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin-bottom: 1.5rem;
            background-color: white;
        }}
        .status-card h3 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        .status-card p {{
            font-size: 1.1rem;
            color: var(--secondary-color);
        }}
        .chart-container {{
            height: 300px;
            margin-bottom: 2rem;
        }}
        .footer {{
            text-align: center;
            padding: 1.5rem 0;
            margin-top: 2rem;
            color: var(--secondary-color);
            font-size: 0.9rem;
        }}
        .nav-pills .nav-link.active {{
            background-color: var(--primary-color);
        }}
        .nav-pills .nav-link {{
            color: var(--primary-color);
        }}
        .badge {{
            font-size: 0.8rem;
            padding: 0.4em 0.6em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1><i class="bi bi-bandaid"></i> Agente Flask Autocurador Supremo</h1>
                    <p class="lead">Relatório de diagnóstico e correção automática</p>
                </div>
                <div class="col-md-4 text-md-end">
                    <p><i class="bi bi-calendar3"></i> {timestamp}</p>
                    <p><i class="bi bi-folder"></i> {project_name}</p>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="row">
            <div class="col-md-4">
                <div class="status-card" style="border-left: 5px solid var(--primary-color);">
                    <i class="bi bi-search" style="font-size: 2rem; color: var(--primary-color);"></i>
                    <h3>{total_issues}</h3>
                    <p>Problemas Detectados</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="status-card" style="border-left: 5px solid var(--success-color);">
                    <i class="bi bi-wrench" style="font-size: 2rem; color: var(--success-color);"></i>
                    <h3>{total_fixes}</h3>
                    <p>Correções Aplicadas</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="status-card" style="border-left: 5px solid var(--info-color);">
                    <i class="bi bi-lightning" style="font-size: 2rem; color: var(--info-color);"></i>
                    <h3>{self.structure['pattern']}</h3>
                    <p>Padrão de Projeto</p>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <i class="bi bi-info-circle"></i> Estrutura do Projeto
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h5>Informações Gerais</h5>
                                <ul class="list-group list-group-flush">
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Padrão de Projeto
                                        <span class="badge bg-primary">{self.structure['pattern']}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Banco de Dados
                                        <span class="badge bg-primary">{self.structure['database']['type']}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Sistema de Autenticação
                                        <span class="badge bg-primary">{self.structure['auth']['type']}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Arquivos de Aplicação
                                        <span class="badge bg-primary">{len(self.structure['app_files'])}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Blueprints
                                        <span class="badge bg-primary">{len(self.structure['blueprint_files'])}</span>
                                    </li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h5>Componentes Detectados</h5>
                                <ul class="list-group list-group-flush">
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Templates
                                        <span class="badge bg-primary">{len(self.detector.get_templates())}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Rotas
                                        <span class="badge bg-primary">{len(self.detector.get_routes())}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Modelos
                                        <span class="badge bg-primary">{len(self.detector.get_models())}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Arquivos de Configuração
                                        <span class="badge bg-primary">{len(self.structure['config_files'])}</span>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <i class="bi bi-exclamation-triangle"></i> Problemas Detectados
                    </div>
                    <div class="card-body">
                        <ul class="nav nav-pills mb-3" id="issues-tab" role="tablist">
"""

        # Adiciona abas para cada categoria de problemas
        for i, category in enumerate(self.issues.keys()):
            active = "active" if i == 0 else ""
            selected = "true" if i == 0 else "false"
            count = len(self.issues[category])
            html += f"""
                            <li class="nav-item" role="presentation">
                                <button class="nav-link {active}" id="{category}-tab" data-bs-toggle="pill" data-bs-target="#{category}-content" type="button" role="tab" aria-controls="{category}-content" aria-selected="{selected}">
                                    {category.capitalize()} <span class="badge bg-secondary">{count}</span>
                                </button>
                            </li>"""

        html += """
                        </ul>
                        <div class="tab-content" id="issues-tabContent">
"""

        # Adiciona conteúdo para cada categoria de problemas
        for i, category in enumerate(self.issues.keys()):
            active = "show active" if i == 0 else ""
            html += f"""
                            <div class="tab-pane fade {active}" id="{category}-content" role="tabpanel" aria-labelledby="{category}-tab">
"""

            if not self.issues[category]:
                html += """
                                <div class="alert alert-success" role="alert">
                                    <i class="bi bi-check-circle"></i> Nenhum problema detectado nesta categoria.
                                </div>
"""
            else:
                html += """
                                <div class="table-responsive">
                                    <table class="table table-hover">
                                        <thead>
                                            <tr>
                                                <th>Tipo</th>
                                                <th>Descrição</th>
                                                <th>Arquivo</th>
                                                <th>Severidade</th>
                                            </tr>
                                        </thead>
                                        <tbody>
"""

                for issue in self.issues[category]:
                    severity_class = {
                        "high": "severity-high",
                        "medium": "severity-medium",
                        "low": "severity-low"
                    }.get(issue.get("severity", "medium"), "")
                    
                    file_path = issue.get("file", "")
                    if file_path:
                        file_path = Path(file_path).name
                    
                    html += f"""
                                            <tr>
                                                <td>{issue.get("type", "")}</td>
                                                <td>{issue.get("description", "")}</td>
                                                <td>{file_path}</td>
                                                <td class="{severity_class}">{issue.get("severity", "medium")}</td>
                                            </tr>
"""

                html += """
                                        </tbody>
                                    </table>
                                </div>
"""

            html += """
                            </div>
"""

        html += """
                        </div>
                    </div>
                </div>
            </div>
        </div>
"""

        # Adiciona seção de correções se disponível
        if self.healing:
            html += """
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <i class="bi bi-wrench"></i> Correções Aplicadas
                    </div>
                    <div class="card-body">
                        <ul class="nav nav-pills mb-3" id="fixes-tab" role="tablist">
"""

            # Adiciona abas para cada categoria de correções
            for i, category in enumerate(self.fixes.keys()):
                active = "active" if i == 0 else ""
                selected = "true" if i == 0 else "false"
                count = len(self.fixes[category])
                html += f"""
                            <li class="nav-item" role="presentation">
                                <button class="nav-link {active}" id="fix-{category}-tab" data-bs-toggle="pill" data-bs-target="#fix-{category}-content" type="button" role="tab" aria-controls="fix-{category}-content" aria-selected="{selected}">
                                    {category.capitalize()} <span class="badge bg-secondary">{count}</span>
                                </button>
                            </li>"""

            html += """
                        </ul>
                        <div class="tab-content" id="fixes-tabContent">
"""

            # Adiciona conteúdo para cada categoria de correções
            for i, category in enumerate(self.fixes.keys()):
                active = "show active" if i == 0 else ""
                html += f"""
                            <div class="tab-pane fade {active}" id="fix-{category}-content" role="tabpanel" aria-labelledby="fix-{category}-tab">
"""

                if not self.fixes[category]:
                    html += """
                                <div class="alert alert-info" role="alert">
                                    <i class="bi bi-info-circle"></i> Nenhuma correção aplicada nesta categoria.
                                </div>
"""
                else:
                    html += """
                                <div class="table-responsive">
                                    <table class="table table-hover">
                                        <thead>
                                            <tr>
                                                <th>Tipo</th>
                                                <th>Descrição</th>
                                                <th>Arquivo</th>
                                            </tr>
                                        </thead>
                                        <tbody>
"""

                    for fix in self.fixes[category]:
                        file_path = fix.get("file", "")
                        if file_path:
                            file_path = Path(file_path).name
                        
                        html += f"""
                                            <tr>
                                                <td>{fix.get("type", "")}</td>
                                                <td>{fix.get("description", "")}</td>
                                                <td>{file_path}</td>
                                            </tr>
"""

                    html += """
                                        </tbody>
                                    </table>
                                </div>
"""

                html += """
                            </div>
"""

            html += """
                        </div>
                    </div>
                </div>
            </div>
        </div>
"""

        # Adiciona gráficos e visualizações
        html += """
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <i class="bi bi-pie-chart"></i> Distribuição de Problemas
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="issuesChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <i class="bi bi-bar-chart"></i> Severidade dos Problemas
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="severityChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
"""

        # Adiciona rodapé e scripts
        html += """
        <div class="footer">
            <p>Gerado pelo Agente Flask Autocurador Supremo Universal</p>
            <p><small>© 2025 Manus AI</small></p>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // Dados para os gráficos
        const issuesData = {
"""

        # Adiciona dados para o gráfico de distribuição de problemas
        categories = []
        counts = []
        for category in self.issues:
            categories.append(category.capitalize())
            counts.append(len(self.issues[category]))

        html += f"""
            labels: {json.dumps(categories)},
            datasets: [{{
                data: {json.dumps(counts)},
                backgroundColor: [
                    '#007bff',
                    '#28a745',
                    '#ffc107',
                    '#dc3545',
                    '#17a2b8',
                    '#6c757d'
                ],
                borderWidth: 1
            }}]
        }};

        // Dados para o gráfico de severidade
        const severityData = {{
            labels: ['Alta', 'Média', 'Baixa'],
            datasets: [{{
                data: [
"""

        # Conta problemas por severidade
        high = 0
        medium = 0
        low = 0
        for category in self.issues:
            for issue in self.issues[category]:
                severity = issue.get("severity", "medium")
                if severity == "high":
                    high += 1
                elif severity == "medium":
                    medium += 1
                elif severity == "low":
                    low += 1

        html += f"""
                    {high}, {medium}, {low}
                ],
                backgroundColor: [
                    '#dc3545',
                    '#ffc107',
                    '#17a2b8'
                ],
                borderWidth: 1
            }}]
        }};

        // Renderiza os gráficos
        window.addEventListener('load', function() {{
            // Gráfico de distribuição de problemas
            const issuesCtx = document.getElementById('issuesChart').getContext('2d');
            new Chart(issuesCtx, {{
                type: 'pie',
                data: issuesData,
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'right',
                        }}
                    }}
                }}
            }});

            // Gráfico de severidade
            const severityCtx = document.getElementById('severityChart').getContext('2d');
            new Chart(severityCtx, {{
                type: 'bar',
                data: severityData,
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            display: false
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{
                                precision: 0
                            }}
                        }}
                    }}
                }}
            }});
        }});
    </script>
</body>
</html>
"""

        return html
