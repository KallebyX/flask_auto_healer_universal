#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de diagnóstico universal para projetos Flask.

Este módulo contém classes e funções para diagnosticar problemas
em qualquer projeto Flask, independente do padrão utilizado.
"""

import os
import re
import ast
import inspect
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional, Union

from .detector import FlaskProjectDetector


class DiagnosticEngine:
    """
    Motor de diagnóstico para projetos Flask.
    
    Esta classe é responsável por analisar e identificar problemas
    em um projeto Flask, independente do padrão utilizado.
    """
    
    def __init__(self, detector: FlaskProjectDetector):
        """
        Inicializa o motor de diagnóstico com um detector.
        
        Args:
            detector: Detector de estrutura de projetos Flask.
        """
        self.detector = detector
        self.structure = detector.detected_structure
        self.issues = {
            'routes': [],
            'templates': [],
            'database': [],
            'code': [],
            'security': [],
            'performance': []
        }
        self.logger = logging.getLogger('flask_auto_healer.diagnostic')
    
    def diagnose(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Executa o diagnóstico completo do projeto.
        
        Returns:
            Dict contendo os problemas encontrados.
        """
        self._diagnose_routes()
        self._diagnose_templates()
        self._diagnose_database()
        self._diagnose_code()
        self._diagnose_security()
        self._diagnose_performance()
        
        return self.issues
    
    def _diagnose_routes(self) -> None:
        """
        Diagnostica problemas nas rotas.
        """
        self.logger.info("Diagnosticando rotas...")
        
        # Obtém todas as rotas
        routes = self.detector.get_routes()
        
        # Verifica funções de rota sem return
        for route_file in self.structure['route_files']:
            try:
                with open(route_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Analisa o código com AST
                    tree = ast.parse(content)
                    
                    # Procura por funções de rota
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Verifica se é uma função de rota
                            is_route = False
                            for decorator in node.decorator_list:
                                if isinstance(decorator, ast.Call):
                                    if isinstance(decorator.func, ast.Attribute):
                                        if decorator.func.attr == 'route':
                                            is_route = True
                                            break
                            
                            if is_route:
                                # Verifica se a função tem return
                                has_return = False
                                for child in ast.walk(node):
                                    if isinstance(child, ast.Return):
                                        has_return = True
                                        break
                                
                                if not has_return:
                                    self.issues['routes'].append({
                                        'type': 'missing_return',
                                        'file': route_file,
                                        'function': node.name,
                                        'line': node.lineno,
                                        'description': f"Função de rota '{node.name}' não possui return",
                                        'severity': 'high'
                                    })
            except Exception as e:
                self.logger.error(f"Erro ao analisar arquivo {route_file}: {str(e)}")
        
        # Verifica rotas duplicadas
        route_paths = {}
        for route in routes:
            path = route['path']
            if path in route_paths:
                self.issues['routes'].append({
                    'type': 'duplicate_route',
                    'file': route['file'],
                    'path': path,
                    'function': route['function'],
                    'description': f"Rota duplicada: {path}",
                    'severity': 'high'
                })
            else:
                route_paths[path] = route
        
        # Verifica rotas sem métodos HTTP especificados
        for route in routes:
            if not route.get('methods'):
                self.issues['routes'].append({
                    'type': 'unspecified_methods',
                    'file': route['file'],
                    'path': route['path'],
                    'function': route['function'],
                    'description': f"Rota '{route['path']}' não especifica métodos HTTP",
                    'severity': 'medium'
                })
    
    def _diagnose_templates(self) -> None:
        """
        Diagnostica problemas nos templates.
        """
        self.logger.info("Diagnosticando templates...")
        
        # Obtém todos os templates
        templates = self.detector.get_templates()
        template_references = self.detector.get_template_references()
        
        # Verifica templates referenciados mas não existentes
        for template_name, references in template_references.items():
            template_exists = False
            for template in templates:
                if template['relative_path'] == template_name or template['name'] == template_name:
                    template_exists = True
                    break
            
            if not template_exists:
                self.issues['templates'].append({
                    'type': 'missing_template',
                    'template': template_name,
                    'references': references,
                    'description': f"Template '{template_name}' é referenciado mas não existe",
                    'severity': 'high'
                })
        
        # Verifica templates com problemas de sintaxe Jinja
        for template in templates:
            try:
                with open(template['path'], 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Verifica blocos não fechados
                    blocks = re.findall(r'{%\s*block\s+(\w+)\s*%}', content)
                    for block in blocks:
                        if not re.search(r'{%\s*endblock\s*(?:' + block + r')?\s*%}', content):
                            self.issues['templates'].append({
                                'type': 'unclosed_block',
                                'template': template['relative_path'],
                                'block': block,
                                'description': f"Bloco '{block}' não fechado no template '{template['relative_path']}'",
                                'severity': 'high'
                            })
                    
                    # Verifica referências a url_for inválidas
                    url_for_refs = re.findall(r'url_for\(\s*[\'"]([^\'"]+)[\'"]', content)
                    for ref in url_for_refs:
                        # Verifica se o endpoint existe nas rotas
                        endpoint_exists = False
                        for route in self.detector.get_routes():
                            if route['function'] == ref or f"{route['app_or_blueprint']}.{route['function']}" == ref:
                                endpoint_exists = True
                                break
                        
                        if not endpoint_exists:
                            self.issues['templates'].append({
                                'type': 'invalid_url_for',
                                'template': template['relative_path'],
                                'endpoint': ref,
                                'description': f"Referência a endpoint inexistente '{ref}' no template '{template['relative_path']}'",
                                'severity': 'high'
                            })
            except Exception as e:
                self.logger.error(f"Erro ao analisar template {template['path']}: {str(e)}")
        
        # Verifica templates não utilizados
        for template in templates:
            template_used = False
            for referenced_template in template_references.keys():
                if template['relative_path'] == referenced_template or template['name'] == referenced_template:
                    template_used = True
                    break
            
            if not template_used:
                self.issues['templates'].append({
                    'type': 'unused_template',
                    'template': template['relative_path'],
                    'description': f"Template '{template['relative_path']}' não é referenciado em nenhum lugar",
                    'severity': 'low'
                })
    
    def _diagnose_database(self) -> None:
        """
        Diagnostica problemas no banco de dados.
        """
        self.logger.info("Diagnosticando banco de dados...")
        
        # Verifica se há configuração de banco de dados
        if self.structure['database']['type'] == 'none':
            self.issues['database'].append({
                'type': 'no_database',
                'description': "Nenhuma configuração de banco de dados encontrada",
                'severity': 'medium'
            })
            return
        
        # Obtém todos os modelos
        models = self.detector.get_models()
        
        # Verifica modelos sem campos
        for model in models:
            if not model['fields']:
                self.issues['database'].append({
                    'type': 'empty_model',
                    'file': model['file'],
                    'model': model['name'],
                    'description': f"Modelo '{model['name']}' não possui campos",
                    'severity': 'medium'
                })
        
        # Verifica se há modelos relacionados a usuários sem campos de senha
        for model in models:
            if 'user' in model['name'].lower() or 'usuario' in model['name'].lower():
                has_password_field = False
                for field in model['fields']:
                    if 'password' in field.lower() or 'senha' in field.lower():
                        has_password_field = True
                        break
                
                if not has_password_field:
                    self.issues['database'].append({
                        'type': 'user_model_without_password',
                        'file': model['file'],
                        'model': model['name'],
                        'description': f"Modelo de usuário '{model['name']}' não possui campo de senha",
                        'severity': 'medium'
                    })
    
    def _diagnose_code(self) -> None:
        """
        Diagnostica problemas no código.
        """
        self.logger.info("Diagnosticando código...")
        
        # Verifica imports não utilizados
        for file_path in self.structure['app_files']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Analisa o código com AST
                    tree = ast.parse(content)
                    
                    # Coleta todos os imports
                    imports = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for name in node.names:
                                imports.append({
                                    'name': name.name,
                                    'asname': name.asname,
                                    'line': node.lineno,
                                    'node': node
                                })
                        elif isinstance(node, ast.ImportFrom):
                            for name in node.names:
                                imports.append({
                                    'name': f"{node.module}.{name.name}" if node.module else name.name,
                                    'asname': name.asname,
                                    'line': node.lineno,
                                    'node': node
                                })
                    
                    # Coleta todos os nomes utilizados
                    used_names = set()
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Name):
                            used_names.add(node.id)
                        elif isinstance(node, ast.Attribute):
                            if isinstance(node.value, ast.Name):
                                used_names.add(node.value.id)
                    
                    # Verifica imports não utilizados
                    for imp in imports:
                        name_to_check = imp['asname'] if imp['asname'] else imp['name'].split('.')[-1]
                        if name_to_check not in used_names:
                            self.issues['code'].append({
                                'type': 'unused_import',
                                'file': file_path,
                                'import': imp['name'],
                                'line': imp['line'],
                                'description': f"Import não utilizado: {imp['name']}",
                                'severity': 'low'
                            })
            except Exception as e:
                self.logger.error(f"Erro ao analisar arquivo {file_path}: {str(e)}")
        
        # Verifica variáveis não utilizadas
        for file_path in self.structure['app_files']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Analisa o código com AST
                    tree = ast.parse(content)
                    
                    # Coleta todas as atribuições
                    assignments = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Assign):
                            for target in node.targets:
                                if isinstance(target, ast.Name):
                                    assignments.append({
                                        'name': target.id,
                                        'line': node.lineno
                                    })
                    
                    # Coleta todos os nomes utilizados
                    used_names = set()
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                            used_names.add(node.id)
                    
                    # Verifica variáveis não utilizadas
                    for assignment in assignments:
                        if assignment['name'] not in used_names and not assignment['name'].startswith('_'):
                            self.issues['code'].append({
                                'type': 'unused_variable',
                                'file': file_path,
                                'variable': assignment['name'],
                                'line': assignment['line'],
                                'description': f"Variável não utilizada: {assignment['name']}",
                                'severity': 'low'
                            })
            except Exception as e:
                self.logger.error(f"Erro ao analisar arquivo {file_path}: {str(e)}")
    
    def _diagnose_security(self) -> None:
        """
        Diagnostica problemas de segurança.
        """
        self.logger.info("Diagnosticando segurança...")
        
        # Verifica hardcoded secrets
        for file_path in self.structure['app_files'] + self.structure['config_files']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Procura por padrões de secrets
                    secret_patterns = [
                        (r'SECRET_KEY\s*=\s*[\'"]([^\'"]{10,})[\'"]', 'SECRET_KEY hardcoded'),
                        (r'password\s*=\s*[\'"]([^\'"]{6,})[\'"]', 'Senha hardcoded'),
                        (r'api_key\s*=\s*[\'"]([^\'"]{10,})[\'"]', 'API key hardcoded'),
                        (r'token\s*=\s*[\'"]([^\'"]{10,})[\'"]', 'Token hardcoded')
                    ]
                    
                    for pattern, description in secret_patterns:
                        for match in re.finditer(pattern, content, re.IGNORECASE):
                            self.issues['security'].append({
                                'type': 'hardcoded_secret',
                                'file': file_path,
                                'line': content[:match.start()].count('\n') + 1,
                                'description': description,
                                'severity': 'high'
                            })
            except Exception as e:
                self.logger.error(f"Erro ao analisar arquivo {file_path}: {str(e)}")
        
        # Verifica configurações de segurança
        for file_path in self.structure['app_files'] + self.structure['config_files']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Procura por configurações inseguras
                    insecure_configs = [
                        (r'DEBUG\s*=\s*True', 'DEBUG=True em produção é inseguro'),
                        (r'TESTING\s*=\s*True', 'TESTING=True em produção é inseguro'),
                        (r'WTF_CSRF_ENABLED\s*=\s*False', 'CSRF proteção desativada'),
                        (r'SQLALCHEMY_TRACK_MODIFICATIONS\s*=\s*True', 'SQLALCHEMY_TRACK_MODIFICATIONS=True impacta performance')
                    ]
                    
                    for pattern, description in insecure_configs:
                        if re.search(pattern, content):
                            self.issues['security'].append({
                                'type': 'insecure_config',
                                'file': file_path,
                                'description': description,
                                'severity': 'medium'
                            })
            except Exception as e:
                self.logger.error(f"Erro ao analisar arquivo {file_path}: {str(e)}")
    
    def _diagnose_performance(self) -> None:
        """
        Diagnostica problemas de performance.
        """
        self.logger.info("Diagnosticando performance...")
        
        # Verifica queries N+1 potenciais
        for file_path in self.structure['route_files']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Procura por padrões de loop com query
                    for match in re.finditer(r'for\s+\w+\s+in\s+(\w+)(?:\.query)?\.(?:all|filter)', content):
                        # Verifica se há query dentro do loop
                        loop_start = match.end()
                        next_line = content[loop_start:].find('\n')
                        if next_line == -1:
                            next_line = len(content) - loop_start
                        
                        loop_body_start = loop_start + next_line
                        # Encontra o fim do loop (indentação)
                        loop_body = content[loop_body_start:]
                        loop_lines = loop_body.split('\n')
                        
                        in_loop = False
                        for i, line in enumerate(loop_lines):
                            if i == 0 or line.strip() == '':
                                continue
                            
                            if not line.startswith(' ') and not line.startswith('\t'):
                                break
                            
                            in_loop = True
                            if '.query' in line or '.filter' in line or '.get(' in line:
                                self.issues['performance'].append({
                                    'type': 'n_plus_1_query',
                                    'file': file_path,
                                    'line': content[:loop_start].count('\n') + i + 1,
                                    'description': "Potencial problema de N+1 query detectado",
                                    'severity': 'medium'
                                })
                                break
            except Exception as e:
                self.logger.error(f"Erro ao analisar arquivo {file_path}: {str(e)}")
        
        # Verifica uso de eager loading
        for file_path in self.structure['route_files']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Verifica se há relacionamentos sem eager loading
                    if '.query.' in content and '.join(' not in content and '.options(' not in content:
                        self.issues['performance'].append({
                            'type': 'missing_eager_loading',
                            'file': file_path,
                            'description': "Consultas sem eager loading podem causar problemas de performance",
                            'severity': 'low'
                        })
            except Exception as e:
                self.logger.error(f"Erro ao analisar arquivo {file_path}: {str(e)}")


# Função auxiliar para diagnóstico rápido
def diagnose_flask_project(detector: FlaskProjectDetector) -> Dict[str, List[Dict[str, Any]]]:
    """
    Diagnostica problemas em um projeto Flask.
    
    Args:
        detector: Detector de estrutura de projetos Flask.
        
    Returns:
        Dict contendo os problemas encontrados.
    """
    engine = DiagnosticEngine(detector)
    return engine.diagnose()


if __name__ == "__main__":
    # Exemplo de uso
    import sys
    from detector import FlaskProjectDetector
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "."
    
    detector = FlaskProjectDetector(project_path)
    detector.detect()
    
    issues = diagnose_flask_project(detector)
    
    import json
    print(json.dumps(issues, indent=2))
