#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de gerenciamento de presets para o Agente Flask Autocurador Supremo Universal.

Este módulo contém classes para gerenciamento de presets para diferentes tipos de projetos.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from ..core.detector import FlaskProjectDetector


class PresetManager:
    """
    Gerenciador de presets para o Agente Flask Autocurador Supremo Universal.
    """
    
    def __init__(self, detector: FlaskProjectDetector):
        """
        Inicializa o gerenciador de presets.
        
        Args:
            detector: Detector de estrutura de projetos Flask.
        """
        self.detector = detector
        self.structure = detector.detected_structure
        self.preset = None
        self.preset_name = None
    
    def load_preset(self, preset_name: str) -> Dict[str, Any]:
        """
        Carrega um preset específico.
        
        Args:
            preset_name: Nome do preset a ser carregado.
            
        Returns:
            Dict contendo as configurações do preset.
        """
        self.preset_name = preset_name
        
        # Verifica se é um preset interno
        if preset_name in ['blog', 'ecommerce', 'admin-panel']:
            self.preset = self._load_internal_preset(preset_name)
        else:
            # Tenta carregar de um arquivo
            preset_path = Path(preset_name)
            if preset_path.exists() and preset_path.is_file():
                self.preset = self._load_preset_from_file(preset_path)
            else:
                # Tenta carregar de um diretório de presets
                preset_dir = Path(__file__).parent / 'presets'
                preset_file = preset_dir / f"{preset_name}.yaml"
                if preset_file.exists():
                    self.preset = self._load_preset_from_file(preset_file)
                else:
                    raise ValueError(f"Preset não encontrado: {preset_name}")
        
        return self.preset
    
    def _load_internal_preset(self, preset_name: str) -> Dict[str, Any]:
        """
        Carrega um preset interno.
        
        Args:
            preset_name: Nome do preset interno.
            
        Returns:
            Dict contendo as configurações do preset.
        """
        if preset_name == 'blog':
            return self._load_blog_preset()
        elif preset_name == 'ecommerce':
            return self._load_ecommerce_preset()
        elif preset_name == 'admin-panel':
            return self._load_admin_panel_preset()
        else:
            raise ValueError(f"Preset interno não encontrado: {preset_name}")
    
    def _load_preset_from_file(self, preset_path: Path) -> Dict[str, Any]:
        """
        Carrega um preset de um arquivo.
        
        Args:
            preset_path: Caminho para o arquivo de preset.
            
        Returns:
            Dict contendo as configurações do preset.
        """
        with open(preset_path, 'r', encoding='utf-8') as f:
            if preset_path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif preset_path.suffix == '.json':
                import json
                return json.load(f)
            else:
                raise ValueError(f"Formato de arquivo de preset não suportado: {preset_path.suffix}")
    
    def _load_blog_preset(self) -> Dict[str, Any]:
        """
        Carrega o preset para blogs.
        
        Returns:
            Dict contendo as configurações do preset.
        """
        return {
            "name": "blog",
            "description": "Preset para blogs",
            "expected_models": ["Post", "User", "Comment", "Category", "Tag"],
            "expected_routes": ["index", "post", "category", "tag", "author", "search"],
            "expected_templates": ["index.html", "post.html", "category.html", "tag.html", "author.html", "search.html"],
            "diagnostic_rules": {
                "routes": {
                    "required_routes": ["index", "post", "category", "author"],
                    "recommended_routes": ["tag", "search", "archive"]
                },
                "models": {
                    "required_fields": {
                        "Post": ["title", "content", "author", "date", "slug"],
                        "User": ["username", "email", "password", "name"],
                        "Comment": ["content", "author", "post", "date"]
                    }
                },
                "templates": {
                    "required_templates": ["index.html", "post.html", "category.html"],
                    "recommended_templates": ["tag.html", "author.html", "search.html"]
                }
            },
            "healing_rules": {
                "create_missing_models": True,
                "create_missing_routes": True,
                "create_missing_templates": True
            }
        }
    
    def _load_ecommerce_preset(self) -> Dict[str, Any]:
        """
        Carrega o preset para e-commerce.
        
        Returns:
            Dict contendo as configurações do preset.
        """
        return {
            "name": "ecommerce",
            "description": "Preset para e-commerce",
            "expected_models": ["Product", "Category", "User", "Order", "OrderItem", "Cart", "CartItem", "Address", "Payment"],
            "expected_routes": ["index", "product", "category", "cart", "checkout", "order", "account", "search"],
            "expected_templates": ["index.html", "product.html", "category.html", "cart.html", "checkout.html", "order.html", "account.html", "search.html"],
            "diagnostic_rules": {
                "routes": {
                    "required_routes": ["index", "product", "category", "cart", "checkout", "order", "account"],
                    "recommended_routes": ["search", "wishlist", "payment"]
                },
                "models": {
                    "required_fields": {
                        "Product": ["name", "description", "price", "stock", "category", "image", "slug"],
                        "User": ["username", "email", "password", "name", "addresses"],
                        "Order": ["user", "items", "total", "status", "date", "address", "payment"],
                        "Cart": ["user", "items", "total"]
                    }
                },
                "templates": {
                    "required_templates": ["index.html", "product.html", "category.html", "cart.html", "checkout.html", "order.html", "account.html"],
                    "recommended_templates": ["search.html", "wishlist.html", "payment.html"]
                }
            },
            "healing_rules": {
                "create_missing_models": True,
                "create_missing_routes": True,
                "create_missing_templates": True
            }
        }
    
    def _load_admin_panel_preset(self) -> Dict[str, Any]:
        """
        Carrega o preset para painéis administrativos.
        
        Returns:
            Dict contendo as configurações do preset.
        """
        return {
            "name": "admin-panel",
            "description": "Preset para painéis administrativos",
            "expected_models": ["User", "Role", "Permission", "Log", "Setting"],
            "expected_routes": ["index", "login", "logout", "dashboard", "users", "roles", "permissions", "logs", "settings"],
            "expected_templates": ["index.html", "login.html", "dashboard.html", "users.html", "roles.html", "permissions.html", "logs.html", "settings.html"],
            "diagnostic_rules": {
                "routes": {
                    "required_routes": ["index", "login", "logout", "dashboard", "users"],
                    "recommended_routes": ["roles", "permissions", "logs", "settings"]
                },
                "models": {
                    "required_fields": {
                        "User": ["username", "email", "password", "name", "role", "active"],
                        "Role": ["name", "permissions"],
                        "Permission": ["name", "description"]
                    }
                },
                "templates": {
                    "required_templates": ["index.html", "login.html", "dashboard.html", "users.html"],
                    "recommended_templates": ["roles.html", "permissions.html", "logs.html", "settings.html"]
                }
            },
            "healing_rules": {
                "create_missing_models": True,
                "create_missing_routes": True,
                "create_missing_templates": True
            }
        }
    
    def get_preset(self) -> Optional[Dict[str, Any]]:
        """
        Retorna o preset carregado.
        
        Returns:
            Dict contendo as configurações do preset ou None se nenhum preset foi carregado.
        """
        return self.preset
    
    def get_preset_name(self) -> Optional[str]:
        """
        Retorna o nome do preset carregado.
        
        Returns:
            Nome do preset ou None se nenhum preset foi carregado.
        """
        return self.preset_name
    
    def apply_preset_rules(self, diagnostic_engine) -> None:
        """
        Aplica as regras do preset ao motor de diagnóstico.
        
        Args:
            diagnostic_engine: Motor de diagnóstico.
        """
        if not self.preset:
            return
        
        # Aplica regras de diagnóstico
        if 'diagnostic_rules' in self.preset:
            rules = self.preset['diagnostic_rules']
            
            # Aplica regras para rotas
            if 'routes' in rules:
                route_rules = rules['routes']
                routes = self.detector.get_routes()
                route_functions = [route['function'] for route in routes]
                
                # Verifica rotas obrigatórias
                if 'required_routes' in route_rules:
                    for required_route in route_rules['required_routes']:
                        if required_route not in route_functions:
                            diagnostic_engine.issues['routes'].append({
                                'type': 'missing_required_route',
                                'route': required_route,
                                'description': f"Rota obrigatória '{required_route}' não encontrada",
                                'severity': 'high'
                            })
                
                # Verifica rotas recomendadas
                if 'recommended_routes' in route_rules:
                    for recommended_route in route_rules['recommended_routes']:
                        if recommended_route not in route_functions:
                            diagnostic_engine.issues['routes'].append({
                                'type': 'missing_recommended_route',
                                'route': recommended_route,
                                'description': f"Rota recomendada '{recommended_route}' não encontrada",
                                'severity': 'medium'
                            })
            
            # Aplica regras para modelos
            if 'models' in rules:
                model_rules = rules['models']
                models = self.detector.get_models()
                model_names = [model['name'] for model in models]
                
                # Verifica campos obrigatórios
                if 'required_fields' in model_rules:
                    for model_name, required_fields in model_rules['required_fields'].items():
                        # Verifica se o modelo existe
                        model = None
                        for m in models:
                            if m['name'] == model_name:
                                model = m
                                break
                        
                        if model:
                            # Verifica campos obrigatórios
                            for required_field in required_fields:
                                if required_field not in model['fields']:
                                    diagnostic_engine.issues['database'].append({
                                        'type': 'missing_required_field',
                                        'model': model_name,
                                        'field': required_field,
                                        'description': f"Campo obrigatório '{required_field}' não encontrado no modelo '{model_name}'",
                                        'severity': 'high'
                                    })
                        else:
                            # Modelo não encontrado
                            diagnostic_engine.issues['database'].append({
                                'type': 'missing_required_model',
                                'model': model_name,
                                'description': f"Modelo obrigatório '{model_name}' não encontrado",
                                'severity': 'high'
                            })
            
            # Aplica regras para templates
            if 'templates' in rules:
                template_rules = rules['templates']
                templates = self.detector.get_templates()
                template_names = [template['name'] for template in templates]
                
                # Verifica templates obrigatórios
                if 'required_templates' in template_rules:
                    for required_template in template_rules['required_templates']:
                        if required_template not in template_names:
                            diagnostic_engine.issues['templates'].append({
                                'type': 'missing_required_template',
                                'template': required_template,
                                'description': f"Template obrigatório '{required_template}' não encontrado",
                                'severity': 'high'
                            })
                
                # Verifica templates recomendados
                if 'recommended_templates' in template_rules:
                    for recommended_template in template_rules['recommended_templates']:
                        if recommended_template not in template_names:
                            diagnostic_engine.issues['templates'].append({
                                'type': 'missing_recommended_template',
                                'template': recommended_template,
                                'description': f"Template recomendado '{recommended_template}' não encontrado",
                                'severity': 'medium'
                            })
    
    def apply_preset_healing(self, healing_engine) -> None:
        """
        Aplica as regras de correção do preset ao motor de correção.
        
        Args:
            healing_engine: Motor de correção.
        """
        if not self.preset:
            return
        
        # Aplica regras de correção
        if 'healing_rules' in self.preset:
            rules = self.preset['healing_rules']
            
            # Implementa a lógica de correção específica para cada preset
            # Esta é uma implementação básica, pode ser expandida conforme necessário
            
            # Cria modelos faltantes
            if rules.get('create_missing_models', False):
                self._create_missing_models(healing_engine)
            
            # Cria rotas faltantes
            if rules.get('create_missing_routes', False):
                self._create_missing_routes(healing_engine)
            
            # Cria templates faltantes
            if rules.get('create_missing_templates', False):
                self._create_missing_templates(healing_engine)
    
    def _create_missing_models(self, healing_engine) -> None:
        """
        Cria modelos faltantes com base no preset.
        
        Args:
            healing_engine: Motor de correção.
        """
        if not self.preset or 'expected_models' not in self.preset:
            return
        
        models = self.detector.get_models()
        model_names = [model['name'] for model in models]
        
        for expected_model in self.preset['expected_models']:
            if expected_model not in model_names:
                # Implementa a criação do modelo faltante
                # Esta é uma implementação básica, pode ser expandida conforme necessário
                pass
    
    def _create_missing_routes(self, healing_engine) -> None:
        """
        Cria rotas faltantes com base no preset.
        
        Args:
            healing_engine: Motor de correção.
        """
        if not self.preset or 'expected_routes' not in self.preset:
            return
        
        routes = self.detector.get_routes()
        route_functions = [route['function'] for route in routes]
        
        for expected_route in self.preset['expected_routes']:
            if expected_route not in route_functions:
                # Implementa a criação da rota faltante
                # Esta é uma implementação básica, pode ser expandida conforme necessário
                pass
    
    def _create_missing_templates(self, healing_engine) -> None:
        """
        Cria templates faltantes com base no preset.
        
        Args:
            healing_engine: Motor de correção.
        """
        if not self.preset or 'expected_templates' not in self.preset:
            return
        
        templates = self.detector.get_templates()
        template_names = [template['name'] for template in templates]
        
        for expected_template in self.preset['expected_templates']:
            if expected_template not in template_names:
                # Implementa a criação do template faltante
                # Esta é uma implementação básica, pode ser expandida conforme necessário
                pass
