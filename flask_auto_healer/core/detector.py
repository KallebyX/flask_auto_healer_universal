#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de detecção automática de estrutura de projetos Flask.

Este módulo contém classes e funções para detectar automaticamente
a estrutura de qualquer projeto Flask, independente do padrão utilizado.
"""

import os
import re
import ast
import importlib.util
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional, Union


class FlaskProjectDetector:
    """
    Detector de estrutura de projetos Flask.
    
    Esta classe é responsável por analisar e identificar a estrutura
    de um projeto Flask, independente do padrão utilizado.
    """
    
    def __init__(self, project_path: Union[str, Path]):
        """
        Inicializa o detector com o caminho do projeto.
        
        Args:
            project_path: Caminho para o diretório raiz do projeto Flask.
        """
        self.project_path = Path(project_path).resolve()
        self.app_files = []
        self.blueprint_files = []
        self.template_dirs = []
        self.static_dirs = []
        self.model_files = []
        self.route_files = []
        self.config_files = []
        self.app_instances = []
        self.factory_functions = []
        self.detected_structure = {}
        self.db_type = None
        self.auth_system = None
    
    def detect(self) -> Dict[str, Any]:
        """
        Executa a detecção completa da estrutura do projeto.
        
        Returns:
            Dict contendo a estrutura detectada do projeto.
        """
        self._find_flask_files()
        self._analyze_app_files()
        self._detect_project_pattern()
        self._detect_database()
        self._detect_auth_system()
        self._build_structure_map()
        
        return self.detected_structure
    
    def _find_flask_files(self) -> None:
        """
        Encontra todos os arquivos Python relevantes no projeto.
        """
        # Diretórios a ignorar
        ignore_dirs = {'.git', '.github', 'venv', 'env', '.venv', '.env', 
                      '__pycache__', 'node_modules', 'migrations', 'tests'}
        
        # Procura por arquivos Python
        for root, dirs, files in os.walk(self.project_path):
            # Filtra diretórios a ignorar
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            # Processa arquivos Python
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        try:
                            content = f.read()
                            
                            # Verifica se é um arquivo relacionado ao Flask
                            if 'import Flask' in content or 'from flask import' in content:
                                self.app_files.append(file_path)
                                
                                # Verifica se contém Blueprint
                                if 'Blueprint(' in content or 'Blueprint (' in content:
                                    self.blueprint_files.append(file_path)
                                
                                # Verifica se contém rotas
                                if '@app.route' in content or '@blueprint.route' in content or '.route(' in content:
                                    self.route_files.append(file_path)
                                
                                # Verifica se contém modelos
                                if 'db.Model' in content or 'SQLAlchemy' in content:
                                    self.model_files.append(file_path)
                                
                                # Verifica se contém configuração
                                if 'app.config' in content or 'Config' in content:
                                    self.config_files.append(file_path)
                        except Exception:
                            # Ignora arquivos que não podem ser lidos
                            pass
            
            # Procura por diretórios de templates e static
            if 'templates' in dirs:
                self.template_dirs.append(Path(root) / 'templates')
            
            if 'static' in dirs:
                self.static_dirs.append(Path(root) / 'static')
    
    def _analyze_app_files(self) -> None:
        """
        Analisa os arquivos de aplicação para identificar instâncias Flask e factory functions.
        """
        for file_path in self.app_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Analisa o código com AST
                    tree = ast.parse(content)
                    
                    # Procura por instâncias Flask
                    for node in ast.walk(tree):
                        # Procura por atribuições como app = Flask(__name__)
                        if isinstance(node, ast.Assign):
                            for target in node.targets:
                                if isinstance(target, ast.Name):
                                    if isinstance(node.value, ast.Call):
                                        if self._is_flask_instance(node.value):
                                            self.app_instances.append({
                                                'file': file_path,
                                                'name': target.id,
                                                'line': node.lineno
                                            })
                        
                        # Procura por funções factory como create_app()
                        if isinstance(node, ast.FunctionDef):
                            if self._is_factory_function(node, content):
                                self.factory_functions.append({
                                    'file': file_path,
                                    'name': node.name,
                                    'line': node.lineno
                                })
            except Exception:
                # Ignora arquivos que não podem ser analisados
                pass
    
    def _is_flask_instance(self, node: ast.Call) -> bool:
        """
        Verifica se um nó AST representa uma instância de Flask.
        
        Args:
            node: Nó AST a ser verificado.
            
        Returns:
            True se o nó representa uma instância de Flask, False caso contrário.
        """
        if hasattr(node, 'func'):
            if isinstance(node.func, ast.Name) and node.func.id == 'Flask':
                return True
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'Flask':
                return True
        return False
    
    def _is_factory_function(self, node: ast.FunctionDef, content: str) -> bool:
        """
        Verifica se uma função é uma factory function de Flask.
        
        Args:
            node: Nó AST da função.
            content: Conteúdo do arquivo.
            
        Returns:
            True se a função é uma factory function, False caso contrário.
        """
        # Verifica se o nome da função sugere uma factory
        factory_names = ['create_app', 'make_app', 'get_app', 'setup_app', 'init_app']
        if node.name in factory_names:
            return True
        
        # Verifica o corpo da função
        function_body = content.split('\n')[node.lineno-1:node.end_lineno]
        function_body = '\n'.join(function_body)
        
        # Verifica se a função cria uma instância de Flask
        if 'Flask(' in function_body and 'return' in function_body:
            return True
        
        return False
    
    def _detect_project_pattern(self) -> None:
        """
        Detecta o padrão de projeto utilizado (monolítico, factory, blueprints).
        """
        # Determina o padrão com base nas análises anteriores
        if self.factory_functions:
            self.detected_structure['pattern'] = 'factory'
            self.detected_structure['factory_function'] = self.factory_functions[0]
        elif self.app_instances:
            if self.blueprint_files:
                self.detected_structure['pattern'] = 'modular'
            else:
                self.detected_structure['pattern'] = 'monolithic'
            self.detected_structure['app_instance'] = self.app_instances[0]
        else:
            self.detected_structure['pattern'] = 'unknown'
    
    def _detect_database(self) -> None:
        """
        Detecta o tipo de banco de dados utilizado.
        """
        db_patterns = {
            'sqlite': [r'sqlite://', r'sqlite:///', r'\.db'],
            'postgresql': [r'postgresql://', r'postgres://', r'psycopg2'],
            'mysql': [r'mysql://', r'pymysql', r'mysqlclient'],
            'mongodb': [r'mongodb://', r'pymongo', r'MongoEngine'],
        }
        
        # Procura por padrões de banco de dados nos arquivos
        for file_path in self.app_files + self.config_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    for db_type, patterns in db_patterns.items():
                        for pattern in patterns:
                            if re.search(pattern, content):
                                self.db_type = db_type
                                self.detected_structure['database'] = {
                                    'type': db_type,
                                    'file': str(file_path)
                                }
                                return
            except Exception:
                pass
        
        # Se não encontrou nenhum padrão específico, mas tem SQLAlchemy
        if self.model_files:
            self.db_type = 'unknown_sql'
            self.detected_structure['database'] = {
                'type': 'unknown_sql',
                'file': str(self.model_files[0]) if self.model_files else None
            }
        else:
            self.detected_structure['database'] = {
                'type': 'none',
                'file': None
            }
    
    def _detect_auth_system(self) -> None:
        """
        Detecta o sistema de autenticação utilizado.
        """
        auth_patterns = {
            'flask_login': [r'flask_login', r'LoginManager', r'current_user'],
            'jwt': [r'jwt', r'JWT', r'JWTManager', r'create_access_token'],
            'oauth': [r'oauth', r'OAuth', r'OAuthlib'],
            'session': [r'session\[', r'session\.'],
        }
        
        # Procura por padrões de autenticação nos arquivos
        for file_path in self.app_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    for auth_type, patterns in auth_patterns.items():
                        for pattern in patterns:
                            if re.search(pattern, content):
                                self.auth_system = auth_type
                                self.detected_structure['auth'] = {
                                    'type': auth_type,
                                    'file': str(file_path)
                                }
                                return
            except Exception:
                pass
        
        self.detected_structure['auth'] = {
            'type': 'none',
            'file': None
        }
    
    def _build_structure_map(self) -> None:
        """
        Constrói o mapa completo da estrutura do projeto.
        """
        self.detected_structure.update({
            'project_path': str(self.project_path),
            'app_files': [str(f) for f in self.app_files],
            'blueprint_files': [str(f) for f in self.blueprint_files],
            'template_dirs': [str(d) for d in self.template_dirs],
            'static_dirs': [str(d) for d in self.static_dirs],
            'model_files': [str(f) for f in self.model_files],
            'route_files': [str(f) for f in self.route_files],
            'config_files': [str(f) for f in self.config_files],
        })
    
    def get_app_instance(self) -> Optional[Dict[str, Any]]:
        """
        Retorna informações sobre a instância da aplicação Flask.
        
        Returns:
            Dicionário com informações da instância ou None se não encontrada.
        """
        if 'app_instance' in self.detected_structure:
            return self.detected_structure['app_instance']
        return None
    
    def get_factory_function(self) -> Optional[Dict[str, Any]]:
        """
        Retorna informações sobre a factory function.
        
        Returns:
            Dicionário com informações da factory function ou None se não encontrada.
        """
        if 'factory_function' in self.detected_structure:
            return self.detected_structure['factory_function']
        return None
    
    def get_blueprints(self) -> List[Dict[str, Any]]:
        """
        Retorna informações sobre os blueprints encontrados.
        
        Returns:
            Lista de dicionários com informações dos blueprints.
        """
        blueprints = []
        
        for file_path in self.blueprint_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Analisa o código com AST
                    tree = ast.parse(content)
                    
                    # Procura por instâncias de Blueprint
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Assign):
                            for target in node.targets:
                                if isinstance(target, ast.Name):
                                    if isinstance(node.value, ast.Call):
                                        if self._is_blueprint_instance(node.value):
                                            # Tenta extrair o nome e o url_prefix
                                            name = None
                                            url_prefix = None
                                            
                                            if node.value.args:
                                                if isinstance(node.value.args[0], ast.Str):
                                                    name = node.value.args[0].s
                                            
                                            for keyword in node.value.keywords:
                                                if keyword.arg == 'url_prefix' and isinstance(keyword.value, ast.Str):
                                                    url_prefix = keyword.value.s
                                            
                                            blueprints.append({
                                                'file': str(file_path),
                                                'name': target.id,
                                                'blueprint_name': name,
                                                'url_prefix': url_prefix,
                                                'line': node.lineno
                                            })
            except Exception:
                # Ignora arquivos que não podem ser analisados
                pass
        
        return blueprints
    
    def _is_blueprint_instance(self, node: ast.Call) -> bool:
        """
        Verifica se um nó AST representa uma instância de Blueprint.
        
        Args:
            node: Nó AST a ser verificado.
            
        Returns:
            True se o nó representa uma instância de Blueprint, False caso contrário.
        """
        if hasattr(node, 'func'):
            if isinstance(node.func, ast.Name) and node.func.id == 'Blueprint':
                return True
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'Blueprint':
                return True
        return False
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """
        Retorna informações sobre as rotas encontradas.
        
        Returns:
            Lista de dicionários com informações das rotas.
        """
        routes = []
        
        for file_path in self.route_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Procura por decoradores de rota
                    route_patterns = [
                        r'@(\w+)\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods=\[([^\]]+)\])?\)',
                        r'@(\w+)\.(?:get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]\)'
                    ]
                    
                    for pattern in route_patterns:
                        for match in re.finditer(pattern, content):
                            app_or_blueprint = match.group(1)
                            route_path = match.group(2)
                            methods = match.group(3) if len(match.groups()) > 2 else None
                            
                            # Encontra a função associada
                            function_match = re.search(rf'{match.group(0)}\s*\ndef\s+(\w+)', content)
                            function_name = function_match.group(1) if function_match else None
                            
                            routes.append({
                                'file': str(file_path),
                                'app_or_blueprint': app_or_blueprint,
                                'path': route_path,
                                'methods': methods,
                                'function': function_name
                            })
            except Exception:
                # Ignora arquivos que não podem ser analisados
                pass
        
        return routes
    
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Retorna informações sobre os modelos encontrados.
        
        Returns:
            Lista de dicionários com informações dos modelos.
        """
        models = []
        
        for file_path in self.model_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Analisa o código com AST
                    tree = ast.parse(content)
                    
                    # Procura por classes que herdam de db.Model
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            for base in node.bases:
                                if (isinstance(base, ast.Attribute) and 
                                    base.attr == 'Model' and 
                                    isinstance(base.value, ast.Name) and 
                                    base.value.id in ['db', 'DB']):
                                    
                                    # Extrai os campos do modelo
                                    fields = []
                                    for class_node in ast.walk(node):
                                        if isinstance(class_node, ast.Assign):
                                            for target in class_node.targets:
                                                if isinstance(target, ast.Name):
                                                    if isinstance(class_node.value, ast.Call):
                                                        if self._is_column_definition(class_node.value):
                                                            fields.append(target.id)
                                    
                                    models.append({
                                        'file': str(file_path),
                                        'name': node.name,
                                        'fields': fields,
                                        'line': node.lineno
                                    })
            except Exception:
                # Ignora arquivos que não podem ser analisados
                pass
        
        return models
    
    def _is_column_definition(self, node: ast.Call) -> bool:
        """
        Verifica se um nó AST representa uma definição de coluna SQLAlchemy.
        
        Args:
            node: Nó AST a ser verificado.
            
        Returns:
            True se o nó representa uma definição de coluna, False caso contrário.
        """
        if hasattr(node, 'func'):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ['Column', 'String', 'Integer', 'Float', 'Boolean', 'Date', 'DateTime']:
                    return True
        return False
    
    def get_templates(self) -> List[Dict[str, Any]]:
        """
        Retorna informações sobre os templates encontrados.
        
        Returns:
            Lista de dicionários com informações dos templates.
        """
        templates = []
        
        for template_dir in self.template_dirs:
            for root, _, files in os.walk(template_dir):
                for file in files:
                    if file.endswith(('.html', '.jinja', '.jinja2')):
                        template_path = Path(root) / file
                        rel_path = template_path.relative_to(template_dir)
                        
                        templates.append({
                            'path': str(template_path),
                            'relative_path': str(rel_path),
                            'name': file
                        })
        
        return templates
    
    def get_template_references(self) -> Dict[str, List[str]]:
        """
        Retorna referências a templates nos arquivos Python.
        
        Returns:
            Dicionário mapeando templates para arquivos que os referenciam.
        """
        references = {}
        
        for file_path in self.route_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Procura por chamadas a render_template
                    for match in re.finditer(r'render_template\(\s*[\'"]([^\'"]+)[\'"]', content):
                        template_name = match.group(1)
                        
                        if template_name not in references:
                            references[template_name] = []
                        
                        references[template_name].append(str(file_path))
            except Exception:
                # Ignora arquivos que não podem ser analisados
                pass
        
        return references


class FlaskAppLoader:
    """
    Carregador de aplicações Flask.
    
    Esta classe é responsável por carregar dinamicamente uma aplicação Flask
    a partir da estrutura detectada.
    """
    
    def __init__(self, detector: FlaskProjectDetector):
        """
        Inicializa o carregador com um detector.
        
        Args:
            detector: Detector de estrutura de projetos Flask.
        """
        self.detector = detector
        self.app = None
    
    def load_app(self) -> Any:
        """
        Carrega a aplicação Flask.
        
        Returns:
            Instância da aplicação Flask ou None se não for possível carregar.
        """
        structure = self.detector.detected_structure
        
        if structure['pattern'] == 'factory':
            return self._load_from_factory()
        elif structure['pattern'] == 'monolithic' or structure['pattern'] == 'modular':
            return self._load_from_instance()
        
        return None
    
    def _load_from_factory(self) -> Any:
        """
        Carrega a aplicação a partir de uma factory function.
        
        Returns:
            Instância da aplicação Flask ou None se não for possível carregar.
        """
        factory = self.detector.get_factory_function()
        if not factory:
            return None
        
        try:
            # Carrega o módulo que contém a factory
            factory_file = factory['file']
            module_name = os.path.basename(factory_file).replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, factory_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Obtém a factory function
            factory_func = getattr(module, factory['name'])
            
            # Chama a factory function
            app = factory_func()
            self.app = app
            return app
        except Exception:
            return None
    
    def _load_from_instance(self) -> Any:
        """
        Carrega a aplicação a partir de uma instância.
        
        Returns:
            Instância da aplicação Flask ou None se não for possível carregar.
        """
        instance = self.detector.get_app_instance()
        if not instance:
            return None
        
        try:
            # Carrega o módulo que contém a instância
            instance_file = instance['file']
            module_name = os.path.basename(instance_file).replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, instance_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Obtém a instância da aplicação
            app = getattr(module, instance['name'])
            self.app = app
            return app
        except Exception:
            return None


# Função auxiliar para detecção rápida
def detect_flask_project(project_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Detecta a estrutura de um projeto Flask.
    
    Args:
        project_path: Caminho para o diretório raiz do projeto Flask.
        
    Returns:
        Dict contendo a estrutura detectada do projeto.
    """
    detector = FlaskProjectDetector(project_path)
    return detector.detect()


if __name__ == "__main__":
    # Exemplo de uso
    import sys
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "."
    
    structure = detect_flask_project(project_path)
    
    import json
    print(json.dumps(structure, indent=2))
