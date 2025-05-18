#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de relatório Markdown para o Agente Flask Autocurador Supremo Universal.

Este módulo contém a classe para geração de relatórios em formato Markdown.
"""

import os
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from ..core.detector import FlaskProjectDetector
from ..core.diagnostic import DiagnosticEngine


class MarkdownReporter:
    """
    Gerador de relatórios Markdown para o Agente Flask Autocurador Supremo Universal.
    """
    
    def __init__(self, detector: FlaskProjectDetector, diagnostic: DiagnosticEngine):
        """
        Inicializa o gerador de relatórios Markdown.
        
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
        Gera o relatório Markdown.
        
        Args:
            output_path: Caminho para o arquivo de saída.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Gera o conteúdo Markdown
        md_content = self._generate_markdown_content()
        
        # Salva o arquivo
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def _generate_markdown_content(self) -> str:
        """
        Gera o conteúdo Markdown do relatório.
        
        Returns:
            Conteúdo Markdown do relatório.
        """
        # Obtém os dados para o relatório
        project_name = Path(self.structure['project_path']).name
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Conta os problemas e correções
        total_issues = sum(len(self.issues[category]) for category in self.issues)
        total_fixes = 0
        if self.healing:
            total_fixes = sum(len(self.fixes[category]) for category in self.fixes)
        
        # Gera o Markdown
        md = f"""# Relatório do Agente Flask Autocurador Supremo

**Projeto:** {project_name}  
**Data:** {timestamp}  
**Padrão Detectado:** {self.structure['pattern']}

## Resumo

- **Total de Problemas Detectados:** {total_issues}
- **Total de Correções Aplicadas:** {total_fixes}
- **Banco de Dados:** {self.structure['database']['type']}
- **Sistema de Autenticação:** {self.structure['auth']['type']}

## Estrutura do Projeto

O projeto segue o padrão **{self.structure['pattern']}** e possui a seguinte estrutura:

- **Arquivos de Aplicação:** {len(self.structure['app_files'])}
- **Blueprints:** {len(self.structure['blueprint_files'])}
- **Templates:** {len(self.detector.get_templates())}
- **Rotas:** {len(self.detector.get_routes())}
- **Modelos:** {len(self.detector.get_models())}
- **Arquivos de Configuração:** {len(self.structure['config_files'])}

"""

        # Adiciona informações sobre blueprints se existirem
        blueprints = self.detector.get_blueprints()
        if blueprints:
            md += "### Blueprints Detectados\n\n"
            md += "| Nome | URL Prefix | Arquivo |\n"
            md += "|------|------------|--------|\n"
            
            for blueprint in blueprints:
                name = blueprint.get("name", "")
                url_prefix = blueprint.get("url_prefix", "")
                file_path = Path(blueprint.get("file", "")).name
                
                md += f"| {name} | {url_prefix} | {file_path} |\n"
            
            md += "\n"

        # Adiciona informações sobre rotas
        routes = self.detector.get_routes()
        if routes:
            md += "### Rotas Detectadas\n\n"
            md += "| Caminho | Função | Métodos | Blueprint |\n"
            md += "|---------|--------|---------|----------|\n"
            
            for route in routes[:10]:  # Limita a 10 rotas para não sobrecarregar o relatório
                path = route.get("path", "")
                function = route.get("function", "")
                methods = route.get("methods", "")
                app_or_blueprint = route.get("app_or_blueprint", "")
                
                md += f"| {path} | {function} | {methods} | {app_or_blueprint} |\n"
            
            if len(routes) > 10:
                md += f"| ... | ... | ... | ... |\n"
                md += f"*Exibindo 10 de {len(routes)} rotas*\n"
            
            md += "\n"

        # Adiciona informações sobre modelos
        models = self.detector.get_models()
        if models:
            md += "### Modelos Detectados\n\n"
            md += "| Nome | Campos |\n"
            md += "|------|--------|\n"
            
            for model in models:
                name = model.get("name", "")
                fields = ", ".join(model.get("fields", []))
                
                md += f"| {name} | {fields} |\n"
            
            md += "\n"

        # Adiciona seção de problemas
        md += "## Problemas Detectados\n\n"
        
        for category in self.issues:
            if self.issues[category]:
                md += f"### {category.capitalize()}\n\n"
                
                md += "| Tipo | Descrição | Arquivo | Severidade |\n"
                md += "|------|-----------|---------|------------|\n"
                
                for issue in self.issues[category]:
                    issue_type = issue.get("type", "")
                    description = issue.get("description", "")
                    file_path = issue.get("file", "")
                    if file_path:
                        file_path = Path(file_path).name
                    severity = issue.get("severity", "medium")
                    
                    md += f"| {issue_type} | {description} | {file_path} | {severity} |\n"
                
                md += "\n"
            else:
                md += f"### {category.capitalize()}\n\n"
                md += "Nenhum problema detectado nesta categoria.\n\n"

        # Adiciona seção de correções se disponível
        if self.healing:
            md += "## Correções Aplicadas\n\n"
            
            for category in self.fixes:
                if self.fixes[category]:
                    md += f"### {category.capitalize()}\n\n"
                    
                    md += "| Tipo | Descrição | Arquivo |\n"
                    md += "|------|-----------|--------|\n"
                    
                    for fix in self.fixes[category]:
                        fix_type = fix.get("type", "")
                        description = fix.get("description", "")
                        file_path = fix.get("file", "")
                        if file_path:
                            file_path = Path(file_path).name
                        
                        md += f"| {fix_type} | {description} | {file_path} |\n"
                    
                    md += "\n"
                else:
                    md += f"### {category.capitalize()}\n\n"
                    md += "Nenhuma correção aplicada nesta categoria.\n\n"

        # Adiciona seção de recomendações
        md += "## Recomendações\n\n"
        
        if total_issues == 0:
            md += "Parabéns! Seu projeto não apresenta problemas significativos.\n\n"
        else:
            md += "Com base na análise do seu projeto, recomendamos as seguintes ações:\n\n"
            
            if any(len(self.issues[cat]) > 0 for cat in ['routes', 'templates']):
                md += "1. **Revisar a estrutura de rotas e templates** para garantir consistência e evitar problemas de navegação.\n"
            
            if any(len(self.issues[cat]) > 0 for cat in ['database']):
                md += "2. **Verificar a configuração do banco de dados** e garantir que os modelos estejam corretamente definidos.\n"
            
            if any(len(self.issues[cat]) > 0 for cat in ['security']):
                md += "3. **Melhorar a segurança da aplicação** corrigindo os problemas de segurança identificados.\n"
            
            if any(len(self.issues[cat]) > 0 for cat in ['performance']):
                md += "4. **Otimizar a performance** implementando as sugestões para melhorar o desempenho da aplicação.\n"
            
            if any(len(self.issues[cat]) > 0 for cat in ['code']):
                md += "5. **Refatorar o código** para melhorar a qualidade e manutenibilidade.\n"
        
        # Adiciona rodapé
        md += "\n---\n\n"
        md += "*Relatório gerado pelo Agente Flask Autocurador Supremo Universal v1.0.0*\n"
        
        return md
