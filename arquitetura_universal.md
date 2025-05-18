# Arquitetura do Agente Flask Autocurador Supremo Universal

## Visão Geral

O Agente Flask Autocurador Supremo Universal é uma ferramenta avançada para diagnóstico e correção automática de projetos Flask, independente da estrutura específica do projeto. A arquitetura foi projetada para ser modular, extensível e adaptável a qualquer padrão de projeto Flask.

## Componentes Principais

### 1. Núcleo de Detecção (FlaskProjectDetector)

Responsável por analisar e identificar a estrutura do projeto Flask:

- **Detector de Aplicação**: Localiza o ponto de entrada da aplicação Flask (app.py, create_app(), etc.)
- **Detector de Estrutura**: Identifica diretórios importantes (templates, static, routes, models)
- **Analisador de Padrões**: Determina o padrão arquitetural (monolítico, factory, blueprints)
- **Mapeador de Dependências**: Identifica bibliotecas e frameworks utilizados

### 2. Motor de Diagnóstico (DiagnosticEngine)

Analisa o projeto e identifica problemas:

- **Analisador de Rotas**: Verifica endpoints, funções de rota e retornos
- **Analisador de Templates**: Verifica templates, referências e sintaxe Jinja
- **Analisador de Banco de Dados**: Verifica modelos, migrações e conexões
- **Analisador de Código**: Verifica imports, estilo e padrões de código

### 3. Motor de Correção (HealingEngine)

Corrige problemas identificados:

- **Corretor de Rotas**: Corrige endpoints, funções de rota e retornos
- **Corretor de Templates**: Corrige templates, referências e sintaxe Jinja
- **Corretor de Banco de Dados**: Corrige modelos, migrações e conexões
- **Corretor de Código**: Corrige imports, estilo e padrões de código

### 4. Sistema de Presets (PresetManager)

Gerencia presets para diferentes tipos de projetos:

- **Preset Blog**: Configurações e correções específicas para blogs
- **Preset Ecommerce**: Configurações e correções específicas para ecommerce
- **Preset Admin-Panel**: Configurações e correções específicas para painéis administrativos
- **Preset Customizado**: Suporte para presets definidos pelo usuário via JSON/YAML

### 5. Gerador de Relatórios (ReportGenerator)

Gera relatórios em diferentes formatos:

- **Relatório HTML**: Dashboard visual interativo
- **Relatório JSON**: Dados estruturados para integração
- **Relatório Markdown**: Documentação legível
- **Relatório PDF**: Documentação formal
- **Bundle Diagnóstico**: Pacote ZIP com todos os relatórios e logs

### 6. CLI Universal (CommandLineInterface)

Interface de linha de comando avançada:

- **Parser de Argumentos**: Processa opções e flags da CLI
- **Executor de Comandos**: Executa comandos específicos
- **Sistema de Ajuda**: Fornece documentação e exemplos
- **Gerenciador de Configuração**: Gerencia configurações via arquivo ou CLI

### 7. Sistema de Integração (IntegrationSystem)

Permite integração com outras ferramentas:

- **Integração GitHub Actions**: Template para execução em CI/CD
- **Integração GitLab CI/CD**: Template para execução em CI/CD
- **Integração com Plataformas de Deploy**: Suporte para Render, Heroku, Railway
- **API de Integração**: Permite uso como biblioteca em outros projetos

## Fluxo de Execução

1. **Detecção**: O sistema analisa o projeto e identifica sua estrutura
2. **Diagnóstico**: Problemas são identificados em diferentes componentes
3. **Correção**: Problemas são corrigidos automaticamente
4. **Validação**: As correções são validadas para garantir funcionamento
5. **Relatório**: Relatórios são gerados nos formatos solicitados

## Estrutura de Diretórios do Pacote

```
flask_auto_healer/
├── __init__.py
├── __main__.py
├── cli.py
├── core/
│   ├── __init__.py
│   ├── detector.py
│   ├── diagnostic.py
│   ├── healing.py
│   └── validator.py
├── presets/
│   ├── __init__.py
│   ├── base.py
│   ├── blog.py
│   ├── ecommerce.py
│   └── admin_panel.py
├── reporters/
│   ├── __init__.py
│   ├── html_reporter.py
│   ├── json_reporter.py
│   ├── markdown_reporter.py
│   └── pdf_reporter.py
├── integrations/
│   ├── __init__.py
│   ├── github_actions.py
│   ├── gitlab_ci.py
│   └── deploy_platforms.py
├── utils/
│   ├── __init__.py
│   ├── config.py
│   ├── logger.py
│   └── helpers.py
├── templates/
│   ├── reports/
│   └── ci/
└── tests/
    ├── __init__.py
    ├── test_detector.py
    ├── test_diagnostic.py
    └── test_healing.py
```

## Instalação e Uso

### Instalação via PyPI

```bash
pip install flask-auto-healer
# ou
pipx install flask-auto-healer
```

### Uso Básico

```bash
# Execução básica com detecção automática
flask-auto-healer run

# Execução com preset específico
flask-auto-healer run --preset=blog

# Execução com opções específicas
flask-auto-healer run --auto-detect --blueprint-aware --report=html,json

# Geração de relatórios
flask-auto-healer report --format=html,json,md

# Geração de templates CI/CD
flask-auto-healer generate github-workflow
flask-auto-healer generate gitlab-ci
```

### Uso como Biblioteca

```python
from flask_auto_healer import FlaskAutoHealer

# Inicialização
healer = FlaskAutoHealer(project_path="./my_flask_project")

# Detecção
project_structure = healer.detect()

# Diagnóstico
issues = healer.diagnose()

# Correção
fixed_issues = healer.heal()

# Relatório
healer.generate_report(format="html")
```

## Extensibilidade

O sistema foi projetado para ser facilmente extensível:

- **Plugins**: Suporte para plugins de terceiros
- **Presets Customizados**: Definição de presets via arquivos de configuração
- **Regras Personalizadas**: Adição de regras de diagnóstico e correção
- **Relatórios Customizados**: Criação de formatos de relatório personalizados

## Roadmap

1. **Versão 1.0**: Detecção automática, diagnóstico e correção básica
2. **Versão 1.1**: Presets e relatórios avançados
3. **Versão 1.2**: Integração com CI/CD
4. **Versão 1.3**: API de integração e plugins
5. **Versão 2.0**: Suporte para outros frameworks (Django, FastAPI)
