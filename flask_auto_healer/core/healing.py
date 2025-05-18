#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de correção universal para projetos Flask.

Este módulo contém classes e funções para corrigir problemas
em qualquer projeto Flask, independente do padrão utilizado.
"""

import os
import re
import ast
import shutil
import logging
import difflib
import importlib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional, Union

from .detector import FlaskProjectDetector
from .diagnostic import DiagnosticEngine


class HealingEngine:
    """
    Motor de correção para projetos Flask.
    
    Esta classe é responsável por corrigir problemas
    em um projeto Flask, independente do padrão utilizado.
    """
    
    def __init__(self, detector: FlaskProjectDetector, diagnostic: DiagnosticEngine):
        """
        Inicializa o motor de correção com um detector e um diagnóstico.
        
        Args:
            detector: Detector de estrutura de projetos Flask.
            diagnostic: Motor de diagnóstico com problemas identificados.
        """
        self.detector = detector
        self.diagnostic = diagnostic
        self.structure = detector.detected_structure
        self.issues = diagnostic.issues
        self.fixes = {
            'routes': [],
            'templates': [],
            'database': [],
            'code': [],
            'security': [],
            'performance': []
        }
        self.logger = logging.getLogger('flask_auto_healer.healing')
        self.backup_dir = None
    
    def create_backups(self, backup_dir: Optional[str] = None) -> None:
        """
        Cria backups dos arquivos antes de modificá-los.
        
        Args:
            backup_dir: Diretório para armazenar os backups. Se None, usa 'backups' no diretório do projeto.
        """
        if backup_dir:
            self.backup_dir = Path(backup_dir)
        else:
            self.backup_dir = Path(self.structure['project_path']) / 'backups' / f'backup_{int(importlib.import_module("time").time())}'
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Backups serão armazenados em: {self.backup_dir}")
    
    def backup_file(self, file_path: Union[str, Path]) -> None:
        """
        Cria um backup de um arquivo específico.
        
        Args:
            file_path: Caminho do arquivo a ser backupeado.
        """
        if not self.backup_dir:
            self.create_backups()
        
        file_path = Path(file_path)
        relative_path = file_path.relative_to(Path(self.structure['project_path']))
        backup_path = self.backup_dir / relative_path
        
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        self.logger.debug(f"Backup criado: {backup_path}")
    
    def heal(self, create_backups: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        Executa a correção completa do projeto.
        
        Args:
            create_backups: Se True, cria backups dos arquivos antes de modificá-los.
            
        Returns:
            Dict contendo as correções aplicadas.
        """
        if create_backups:
            self.create_backups()
        
        self._heal_routes()
        self._heal_templates()
        self._heal_database()
        self._heal_code()
        self._heal_security()
        self._heal_performance()
        
        return self.fixes
    
    def _heal_routes(self) -> None:
        """
        Corrige problemas nas rotas.
        """
        self.logger.info("Corrigindo rotas...")
        
        # Corrige funções de rota sem return
        for issue in self.issues['routes']:
            if issue['type'] == 'missing_return':
                try:
                    file_path = issue['file']
                    function_name = issue['function']
                    
                    # Faz backup do arquivo
                    self.backup_file(file_path)
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Localiza a função
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and node.name == function_name:
                            # Determina a indentação
                            function_lines = content.split('\n')[node.lineno-1:node.end_lineno]
                            if function_lines:
                                first_line = function_lines[0]
                                indent_match = re.match(r'^(\s*)', first_line)
                                base_indent = indent_match.group(1) if indent_match else ''
                                
                                # Determina a indentação do corpo da função
                                body_indent = base_indent + '    '
                                
                                # Infere o template a ser usado
                                template_name = self._infer_template_for_route(function_name, file_path)
                                
                                # Adiciona return render_template
                                function_end = node.end_lineno - 1
                                lines = content.split('\n')
                                
                                # Verifica se precisa importar render_template
                                if 'render_template' not in content:
                                    # Encontra a última linha de import
                                    last_import_line = 0
                                    for i, line in enumerate(lines):
                                        if line.startswith('import ') or line.startswith('from '):
                                            last_import_line = i
                                    
                                    # Adiciona import de render_template
                                    if 'from flask import' in content:
                                        # Adiciona render_template ao import existente
                                        for i, line in enumerate(lines):
                                            if line.startswith('from flask import'):
                                                if 'render_template' not in line:
                                                    if line.endswith(','):
                                                        lines[i] = line + ' render_template,'
                                                    elif line.endswith(')'):
                                                        lines[i] = line[:-1] + ', render_template)'
                                                    else:
                                                        lines[i] = line + ', render_template'
                                                break
                                    else:
                                        # Adiciona novo import
                                        lines.insert(last_import_line + 1, 'from flask import render_template')
                                
                                # Adiciona return render_template ao final da função
                                return_line = f"{body_indent}return render_template('{template_name}')"
                                
                                # Verifica se a função já tem algum conteúdo
                                if node.body:
                                    # Adiciona após o último statement da função
                                    lines.insert(function_end, return_line)
                                else:
                                    # Função vazia, adiciona como primeiro statement
                                    lines.insert(node.lineno, return_line)
                                
                                # Salva o arquivo modificado
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write('\n'.join(lines))
                                
                                # Registra a correção
                                self.fixes['routes'].append({
                                    'type': 'added_return',
                                    'file': file_path,
                                    'function': function_name,
                                    'template': template_name,
                                    'description': f"Adicionado return render_template('{template_name}') à função {function_name}"
                                })
                                
                                # Verifica se o template existe, se não, cria
                                self._ensure_template_exists(template_name)
                                
                                break
                except Exception as e:
                    self.logger.error(f"Erro ao corrigir função sem return: {str(e)}")
    
    def _infer_template_for_route(self, function_name: str, file_path: str) -> str:
        """
        Infere o nome do template para uma função de rota.
        
        Args:
            function_name: Nome da função de rota.
            file_path: Caminho do arquivo da função.
            
        Returns:
            Nome do template inferido.
        """
        # Tenta inferir o blueprint a partir do nome do arquivo
        file_name = Path(file_path).stem
        blueprint_prefix = ""
        
        # Verifica se o arquivo está em um diretório de blueprint
        file_dir = Path(file_path).parent.name
        if file_dir != 'routes':
            blueprint_prefix = f"{file_dir}/"
        
        # Casos especiais
        if function_name == 'index' or function_name == 'home':
            return f"{blueprint_prefix}index.html"
        
        # Funções CRUD comuns
        crud_mapping = {
            'list': 'list.html',
            'show': 'show.html',
            'create': 'create.html',
            'edit': 'edit.html',
            'delete': 'delete.html'
        }
        
        for crud_action, template_suffix in crud_mapping.items():
            if function_name.startswith(crud_action) or function_name.endswith(crud_action):
                # Extrai o nome do recurso (ex: list_users -> users)
                resource = function_name.replace(crud_action + '_', '').replace('_' + crud_action, '')
                return f"{blueprint_prefix}{resource}/{template_suffix}"
        
        # Padrão geral: usa o nome da função
        return f"{blueprint_prefix}{function_name}.html"
    
    def _ensure_template_exists(self, template_name: str) -> None:
        """
        Garante que um template existe, criando-o se necessário.
        
        Args:
            template_name: Nome do template.
        """
        # Encontra o diretório de templates
        if not self.structure['template_dirs']:
            self.logger.warning(f"Não foi possível criar o template {template_name}: diretório de templates não encontrado")
            return
        
        template_dir = Path(self.structure['template_dirs'][0])
        template_path = template_dir / template_name
        
        # Verifica se o template já existe
        if template_path.exists():
            return
        
        # Cria diretórios intermediários se necessário
        template_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determina o tipo de template a ser criado
        template_content = ""
        
        # Verifica se há um template base
        base_template = "base.html"
        if (template_dir / base_template).exists():
            # Cria template que estende o base
            template_content = f"""{% extends '{base_template}' %}

{% block content %}
<div class="container mt-4">
  <div class="card">
    <div class="card-header">
      <h2>{{ title|default('Página') }}</h2>
    </div>
    <div class="card-body">
      <p>Template gerado automaticamente.</p>
    </div>
  </div>
</div>
{% endblock %}
"""
        else:
            # Cria template standalone
            template_content = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title|default('Página') }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <div class="card">
            <div class="card-header">
                <h2>{{ title|default('Página') }}</h2>
            </div>
            <div class="card-body">
                <p>Template gerado automaticamente.</p>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
        
        # Salva o template
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        self.logger.info(f"Template criado: {template_path}")
        
        # Registra a correção
        self.fixes['templates'].append({
            'type': 'created_template',
            'template': template_name,
            'path': str(template_path),
            'description': f"Criado template {template_name}"
        })
    
    def _heal_templates(self) -> None:
        """
        Corrige problemas nos templates.
        """
        self.logger.info("Corrigindo templates...")
        
        # Corrige templates com blocos não fechados
        for issue in self.issues['templates']:
            if issue['type'] == 'unclosed_block':
                try:
                    template_path = None
                    for template in self.detector.get_templates():
                        if template['relative_path'] == issue['template']:
                            template_path = template['path']
                            break
                    
                    if not template_path:
                        continue
                    
                    # Faz backup do arquivo
                    self.backup_file(template_path)
                    
                    with open(template_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Adiciona endblock
                    if not re.search(r'{%\s*endblock\s*(?:' + issue['block'] + r')?\s*%}', content):
                        # Encontra o bloco
                        block_match = re.search(r'{%\s*block\s+' + issue['block'] + r'\s*%}', content)
                        if block_match:
                            # Encontra o final do conteúdo do bloco (próximo bloco ou final do arquivo)
                            block_start = block_match.end()
                            next_block = re.search(r'{%\s*block\s+', content[block_start:])
                            if next_block:
                                block_end = block_start + next_block.start()
                                content = content[:block_end] + f"{{% endblock {issue['block']} %}}\n" + content[block_end:]
                            else:
                                content += f"\n{{% endblock {issue['block']} %}}"
                            
                            # Salva o arquivo modificado
                            with open(template_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            # Registra a correção
                            self.fixes['templates'].append({
                                'type': 'closed_block',
                                'template': issue['template'],
                                'block': issue['block'],
                                'description': f"Fechado bloco {issue['block']} no template {issue['template']}"
                            })
                except Exception as e:
                    self.logger.error(f"Erro ao corrigir bloco não fechado: {str(e)}")
        
        # Corrige referências a url_for inválidas
        for issue in self.issues['templates']:
            if issue['type'] == 'invalid_url_for':
                try:
                    template_path = None
                    for template in self.detector.get_templates():
                        if template['relative_path'] == issue['template']:
                            template_path = template['path']
                            break
                    
                    if not template_path:
                        continue
                    
                    # Faz backup do arquivo
                    self.backup_file(template_path)
                    
                    with open(template_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Encontra o endpoint mais similar
                    routes = self.detector.get_routes()
                    endpoints = []
                    for route in routes:
                        endpoints.append(route['function'])
                        if route['app_or_blueprint'] and route['function']:
                            endpoints.append(f"{route['app_or_blueprint']}.{route['function']}")
                    
                    if endpoints:
                        # Encontra o endpoint mais similar
                        similar_endpoint = difflib.get_close_matches(issue['endpoint'], endpoints, n=1, cutoff=0.6)
                        if similar_endpoint:
                            # Substitui o endpoint
                            new_content = re.sub(
                                r'url_for\(\s*[\'"]{}\s*[\'"]'.format(re.escape(issue['endpoint'])),
                                f"url_for('{similar_endpoint[0]}'",
                                content
                            )
                            
                            # Salva o arquivo modificado
                            with open(template_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            
                            # Registra a correção
                            self.fixes['templates'].append({
                                'type': 'fixed_url_for',
                                'template': issue['template'],
                                'old_endpoint': issue['endpoint'],
                                'new_endpoint': similar_endpoint[0],
                                'description': f"Corrigido endpoint {issue['endpoint']} para {similar_endpoint[0]} no template {issue['template']}"
                            })
                except Exception as e:
                    self.logger.error(f"Erro ao corrigir url_for inválido: {str(e)}")
        
        # Cria templates faltantes
        for issue in self.issues['templates']:
            if issue['type'] == 'missing_template':
                try:
                    self._ensure_template_exists(issue['template'])
                except Exception as e:
                    self.logger.error(f"Erro ao criar template faltante: {str(e)}")
    
    def _heal_database(self) -> None:
        """
        Corrige problemas no banco de dados.
        """
        self.logger.info("Corrigindo banco de dados...")
        
        # Corrige modelos de usuário sem campo de senha
        for issue in self.issues['database']:
            if issue['type'] == 'user_model_without_password':
                try:
                    file_path = issue['file']
                    model_name = issue['model']
                    
                    # Faz backup do arquivo
                    self.backup_file(file_path)
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Localiza a classe do modelo
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and node.name == model_name:
                            # Determina a indentação
                            model_lines = content.split('\n')[node.lineno-1:node.end_lineno]
                            if model_lines:
                                first_line = model_lines[0]
                                indent_match = re.match(r'^(\s*)', first_line)
                                base_indent = indent_match.group(1) if indent_match else ''
                                
                                # Determina a indentação dos atributos
                                attr_indent = base_indent + '    '
                                
                                # Adiciona campo de senha
                                model_end = node.end_lineno - 1
                                lines = content.split('\n')
                                
                                # Verifica se precisa importar Column e String
                                imports_needed = []
                                if 'Column' not in content:
                                    imports_needed.append('Column')
                                if 'String' not in content:
                                    imports_needed.append('String')
                                
                                if imports_needed:
                                    # Encontra a última linha de import
                                    last_import_line = 0
                                    for i, line in enumerate(lines):
                                        if line.startswith('import ') or line.startswith('from '):
                                            last_import_line = i
                                    
                                    # Adiciona imports necessários
                                    if 'from sqlalchemy import' in content:
                                        # Adiciona ao import existente
                                        for i, line in enumerate(lines):
                                            if line.startswith('from sqlalchemy import'):
                                                for imp in imports_needed:
                                                    if imp not in line:
                                                        if line.endswith(','):
                                                            lines[i] = line + f' {imp},'
                                                        elif line.endswith(')'):
                                                            lines[i] = line[:-1] + f', {imp})'
                                                        else:
                                                            lines[i] = line + f', {imp}'
                                                break
                                    else:
                                        # Adiciona novo import
                                        imports_str = ', '.join(imports_needed)
                                        lines.insert(last_import_line + 1, f'from sqlalchemy import {imports_str}')
                                
                                # Adiciona campo de senha_hash
                                password_field = f"{attr_indent}senha_hash = Column(String(128))"
                                
                                # Adiciona após o último atributo da classe
                                # Encontra a posição adequada (após o último atributo)
                                insert_pos = node.lineno
                                for i in range(node.lineno, node.end_lineno):
                                    line = lines[i] if i < len(lines) else ""
                                    if '=' in line and ('Column(' in line or 'db.Column(' in line):
                                        insert_pos = i + 1
                                
                                lines.insert(insert_pos, password_field)
                                
                                # Salva o arquivo modificado
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write('\n'.join(lines))
                                
                                # Registra a correção
                                self.fixes['database'].append({
                                    'type': 'added_password_field',
                                    'file': file_path,
                                    'model': model_name,
                                    'description': f"Adicionado campo senha_hash ao modelo {model_name}"
                                })
                                
                                break
                except Exception as e:
                    self.logger.error(f"Erro ao adicionar campo de senha: {str(e)}")
    
    def _heal_code(self) -> None:
        """
        Corrige problemas no código.
        """
        self.logger.info("Corrigindo código...")
        
        # Remove imports não utilizados
        for issue in self.issues['code']:
            if issue['type'] == 'unused_import':
                try:
                    file_path = issue['file']
                    import_name = issue['import']
                    
                    # Faz backup do arquivo
                    self.backup_file(file_path)
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    lines = content.split('\n')
                    line_index = issue['line'] - 1
                    
                    if line_index < 0 or line_index >= len(lines):
                        continue
                    
                    line = lines[line_index]
                    
                    # Verifica se é um import simples ou from import
                    if line.startswith('import '):
                        # Import simples
                        if line.strip() == f'import {import_name}':
                            # Remove a linha inteira
                            lines.pop(line_index)
                        else:
                            # Import múltiplo, remove apenas o item
                            parts = line.split('import ')[1].split(',')
                            new_parts = []
                            for part in parts:
                                if part.strip() != import_name:
                                    new_parts.append(part)
                            
                            if new_parts:
                                lines[line_index] = 'import ' + ','.join(new_parts)
                            else:
                                lines.pop(line_index)
                    elif line.startswith('from '):
                        # From import
                        module = line.split('from ')[1].split('import ')[0].strip()
                        imports = line.split('import ')[1].split(',')
                        
                        # Encontra o item específico
                        import_item = import_name.split('.')[-1]
                        new_imports = []
                        for imp in imports:
                            imp = imp.strip()
                            if imp != import_item:
                                new_imports.append(imp)
                        
                        if new_imports:
                            lines[line_index] = f'from {module} import ' + ', '.join(new_imports)
                        else:
                            lines.pop(line_index)
                    
                    # Salva o arquivo modificado
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))
                    
                    # Registra a correção
                    self.fixes['code'].append({
                        'type': 'removed_unused_import',
                        'file': file_path,
                        'import': import_name,
                        'description': f"Removido import não utilizado: {import_name}"
                    })
                except Exception as e:
                    self.logger.error(f"Erro ao remover import não utilizado: {str(e)}")
        
        # Remove variáveis não utilizadas
        for issue in self.issues['code']:
            if issue['type'] == 'unused_variable':
                try:
                    file_path = issue['file']
                    variable_name = issue['variable']
                    
                    # Faz backup do arquivo
                    self.backup_file(file_path)
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Analisa o código com AST
                    tree = ast.parse(content)
                    
                    # Encontra a atribuição da variável
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Assign):
                            for target in node.targets:
                                if isinstance(target, ast.Name) and target.id == variable_name:
                                    # Encontra a linha da atribuição
                                    line_index = node.lineno - 1
                                    lines = content.split('\n')
                                    
                                    # Verifica se é uma atribuição simples
                                    line = lines[line_index]
                                    if re.match(r'^\s*' + variable_name + r'\s*=', line):
                                        # Remove a linha inteira
                                        lines.pop(line_index)
                                        
                                        # Salva o arquivo modificado
                                        with open(file_path, 'w', encoding='utf-8') as f:
                                            f.write('\n'.join(lines))
                                        
                                        # Registra a correção
                                        self.fixes['code'].append({
                                            'type': 'removed_unused_variable',
                                            'file': file_path,
                                            'variable': variable_name,
                                            'description': f"Removida variável não utilizada: {variable_name}"
                                        })
                                        
                                        break
                except Exception as e:
                    self.logger.error(f"Erro ao remover variável não utilizada: {str(e)}")
    
    def _heal_security(self) -> None:
        """
        Corrige problemas de segurança.
        """
        self.logger.info("Corrigindo problemas de segurança...")
        
        # Corrige hardcoded secrets
        for issue in self.issues['security']:
            if issue['type'] == 'hardcoded_secret':
                try:
                    file_path = issue['file']
                    
                    # Faz backup do arquivo
                    self.backup_file(file_path)
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    lines = content.split('\n')
                    line_index = issue['line'] - 1
                    
                    if line_index < 0 or line_index >= len(lines):
                        continue
                    
                    line = lines[line_index]
                    
                    # Verifica se é SECRET_KEY
                    if 'SECRET_KEY' in line:
                        # Substitui por os.environ.get ou valor seguro
                        if 'os.environ.get' not in content:
                            # Adiciona import os se necessário
                            if 'import os' not in content:
                                # Encontra a última linha de import
                                last_import_line = 0
                                for i, line in enumerate(lines):
                                    if line.startswith('import ') or line.startswith('from '):
                                        last_import_line = i
                                
                                # Adiciona import os
                                lines.insert(last_import_line + 1, 'import os')
                        
                        # Substitui a linha
                        lines[line_index] = re.sub(
                            r'SECRET_KEY\s*=\s*[\'"]([^\'"]+)[\'"]',
                            "SECRET_KEY = os.environ.get('SECRET_KEY', 'development-key-CHANGE-ME-in-production')",
                            line
                        )
                    else:
                        # Outros secrets, adiciona comentário de aviso
                        lines[line_index] = line + " # TODO: Mover para variável de ambiente ou arquivo de configuração"
                    
                    # Salva o arquivo modificado
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))
                    
                    # Registra a correção
                    self.fixes['security'].append({
                        'type': 'fixed_hardcoded_secret',
                        'file': file_path,
                        'line': issue['line'],
                        'description': "Corrigido secret hardcoded"
                    })
                except Exception as e:
                    self.logger.error(f"Erro ao corrigir secret hardcoded: {str(e)}")
        
        # Corrige configurações inseguras
        for issue in self.issues['security']:
            if issue['type'] == 'insecure_config':
                try:
                    file_path = issue['file']
                    
                    # Faz backup do arquivo
                    self.backup_file(file_path)
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Corrige configurações específicas
                    if 'DEBUG = True' in content:
                        content = content.replace(
                            'DEBUG = True',
                            "DEBUG = os.environ.get('FLASK_ENV', 'production') != 'production'"
                        )
                    
                    if 'TESTING = True' in content:
                        content = content.replace(
                            'TESTING = True',
                            "TESTING = os.environ.get('FLASK_TESTING', 'False') == 'True'"
                        )
                    
                    if 'WTF_CSRF_ENABLED = False' in content:
                        content = content.replace(
                            'WTF_CSRF_ENABLED = False',
                            "WTF_CSRF_ENABLED = os.environ.get('FLASK_ENV', 'production') == 'production'"
                        )
                    
                    if 'SQLALCHEMY_TRACK_MODIFICATIONS = True' in content:
                        content = content.replace(
                            'SQLALCHEMY_TRACK_MODIFICATIONS = True',
                            'SQLALCHEMY_TRACK_MODIFICATIONS = False'
                        )
                    
                    # Verifica se precisa importar os
                    if ('os.environ.get' in content) and ('import os' not in content):
                        lines = content.split('\n')
                        
                        # Encontra a última linha de import
                        last_import_line = 0
                        for i, line in enumerate(lines):
                            if line.startswith('import ') or line.startswith('from '):
                                last_import_line = i
                        
                        # Adiciona import os
                        lines.insert(last_import_line + 1, 'import os')
                        content = '\n'.join(lines)
                    
                    # Salva o arquivo modificado
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Registra a correção
                    self.fixes['security'].append({
                        'type': 'fixed_insecure_config',
                        'file': file_path,
                        'description': "Corrigida configuração insegura"
                    })
                except Exception as e:
                    self.logger.error(f"Erro ao corrigir configuração insegura: {str(e)}")
    
    def _heal_performance(self) -> None:
        """
        Corrige problemas de performance.
        """
        self.logger.info("Corrigindo problemas de performance...")
        
        # Corrige problemas de N+1 query
        for issue in self.issues['performance']:
            if issue['type'] == 'n_plus_1_query':
                try:
                    file_path = issue['file']
                    
                    # Faz backup do arquivo
                    self.backup_file(file_path)
                    
                    # Adiciona comentário de aviso, não modifica o código diretamente
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    lines = content.split('\n')
                    line_index = issue['line'] - 1
                    
                    if line_index < 0 or line_index >= len(lines):
                        continue
                    
                    # Adiciona comentário de aviso
                    lines[line_index] = lines[line_index] + " # TODO: Potencial problema de N+1 query, considere usar joinedload ou subqueryload"
                    
                    # Salva o arquivo modificado
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))
                    
                    # Registra a correção
                    self.fixes['performance'].append({
                        'type': 'added_n_plus_1_warning',
                        'file': file_path,
                        'line': issue['line'],
                        'description': "Adicionado aviso sobre potencial problema de N+1 query"
                    })
                except Exception as e:
                    self.logger.error(f"Erro ao adicionar aviso de N+1 query: {str(e)}")
        
        # Corrige falta de eager loading
        for issue in self.issues['performance']:
            if issue['type'] == 'missing_eager_loading':
                try:
                    file_path = issue['file']
                    
                    # Faz backup do arquivo
                    self.backup_file(file_path)
                    
                    # Adiciona comentário de aviso, não modifica o código diretamente
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Encontra consultas sem eager loading
                    for match in re.finditer(r'(\w+)\.query\.(?:all|filter|get)\(', content):
                        line_index = content[:match.start()].count('\n')
                        lines = content.split('\n')
                        
                        if line_index >= len(lines):
                            continue
                        
                        # Adiciona comentário de aviso
                        lines[line_index] = lines[line_index] + " # TODO: Considere usar joinedload ou subqueryload para relacionamentos"
                    
                    # Salva o arquivo modificado
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))
                    
                    # Registra a correção
                    self.fixes['performance'].append({
                        'type': 'added_eager_loading_warning',
                        'file': file_path,
                        'description': "Adicionado aviso sobre falta de eager loading"
                    })
                except Exception as e:
                    self.logger.error(f"Erro ao adicionar aviso de eager loading: {str(e)}")


# Função auxiliar para correção rápida
def heal_flask_project(detector: FlaskProjectDetector, diagnostic: DiagnosticEngine, create_backups: bool = True) -> Dict[str, List[Dict[str, Any]]]:
    """
    Corrige problemas em um projeto Flask.
    
    Args:
        detector: Detector de estrutura de projetos Flask.
        diagnostic: Motor de diagnóstico com problemas identificados.
        create_backups: Se True, cria backups dos arquivos antes de modificá-los.
        
    Returns:
        Dict contendo as correções aplicadas.
    """
    engine = HealingEngine(detector, diagnostic)
    return engine.heal(create_backups=create_backups)


if __name__ == "__main__":
    # Exemplo de uso
    import sys
    from detector import FlaskProjectDetector
    from diagnostic import DiagnosticEngine
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "."
    
    detector = FlaskProjectDetector(project_path)
    detector.detect()
    
    diagnostic = DiagnosticEngine(detector)
    issues = diagnostic.diagnose()
    
    fixes = heal_flask_project(detector, diagnostic)
    
    import json
    print(json.dumps(fixes, indent=2))
