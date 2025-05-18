# README.md - Agente Flask Autocurador Supremo

<div align="center">
  <h1>🚀 Agente Flask Autocurador Supremo 🚀</h1>
  <p><strong>Sistema avançado de diagnóstico e correção automática para projetos Flask</strong></p>
</div>

## 📋 Visão Geral

O **Agente Flask Autocurador Supremo** é uma ferramenta poderosa projetada para diagnosticar, corrigir e otimizar automaticamente projetos Flask. Ele identifica e resolve problemas em blueprints, templates, rotas, banco de dados e código Python, garantindo que sua aplicação Flask esteja funcionando perfeitamente.

## ✨ Funcionalidades

- **Diagnóstico Completo**: Analisa todos os aspectos do projeto Flask
- **Autocorreção Inteligente**: Corrige automaticamente erros e problemas detectados
- **Simulação de Uso**: Testa a aplicação com e sem login
- **Validação Abrangente**: Verifica formulários, banco de dados, HTML, lógica e rotas
- **Geração de Relatórios**: Produz logs detalhados e dashboards de status
- **Sugestões com IA**: Utiliza inteligência artificial para problemas complexos
- **Modo Watcher**: Monitora mudanças e corrige em tempo real
- **Simulação de Produção**: Testa performance em ambiente simulado

## 🛠️ Instalação

```bash
# Clone o repositório (opcional)
git clone https://github.com/seu-usuario/flask-autocurador.git
cd flask-autocurador

# Instale as dependências
pip install -r requirements.txt

# Execute o script
python auto_corrigir_sistema.py --corrigir-tudo
```

## 📊 Uso

```bash
# Corrigir tudo automaticamente
python auto_corrigir_sistema.py --corrigir-tudo

# Apenas testar sem fazer correções
python auto_corrigir_sistema.py --somente-testar

# Corrigir apenas templates
python auto_corrigir_sistema.py --templates

# Corrigir rotas e gerar relatório JSON
python auto_corrigir_sistema.py --rotas --relatorio-json

# Executar em modo silencioso
python auto_corrigir_sistema.py --modo-silencioso

# Ativar modo watcher para correções em tempo real
python auto_corrigir_sistema.py --watch

# Simular ambiente de produção com stress test
python auto_corrigir_sistema.py --simulate-prod

# Usar IA para sugestões avançadas
python auto_corrigir_sistema.py --usar-ai
```

## 🔍 Opções Disponíveis

### Escopo de Ação
- `--corrigir-tudo`: Corrige todos os aspectos do projeto
- `--somente-testar`: Apenas testa sem fazer correções
- `--rotas`: Corrige apenas rotas e blueprints
- `--templates`: Corrige apenas templates
- `--banco`: Corrige apenas banco de dados
- `--codigo`: Corrige apenas código Python

### Relatórios
- `--relatorio-html`: Gera relatório em HTML
- `--relatorio-json`: Gera relatório em JSON
- `--relatorio-md`: Gera relatório em Markdown

### Comportamento
- `--modo-silencioso`: Executa sem saída detalhada no console
- `--sem-login`: Não tenta fazer login durante os testes
- `--usar-ai`: Usa IA para sugerir correções avançadas
- `--debug`: Modo de depuração com saída detalhada
- `--watch`: Modo watcher: monitora mudanças e corrige automaticamente
- `--simulate-prod`: Simula ambiente de produção com stress test

### Avançado
- `--diretorio`: Diretório raiz do projeto Flask (padrão: diretório atual)
- `--porta`: Porta para testes (padrão: 5000)
- `--timeout`: Timeout para operações em segundos (padrão: 30)

## 📁 Estrutura de Diretórios

```
/logs/
  ├── diagnostico.log       # Log detalhado de todas as operações
  ├── relatorio.json        # Relatório em formato JSON
  ├── relatorio.html        # Dashboard visual em HTML
  ├── relatorio.md          # Resumo executivo em Markdown
  ├── tracebacks/           # Registros detalhados de erros
  ├── html_dumps/           # Dumps de páginas com erro 500
  └── fix_me_*.py           # Sugestões de correção geradas por IA
```

## 🔄 Fluxo de Execução

1. **Diagnóstico**: Análise completa do projeto Flask
2. **Correção**: Aplicação automática de correções
3. **Teste**: Validação das correções aplicadas
4. **Otimização**: Sugestões de melhorias de performance
5. **Relatório**: Geração de relatórios detalhados

## 📋 Requisitos

- Python 3.9+
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Werkzeug
- Jinja2
- Rich (opcional, para formatação avançada no terminal)
- Faker (opcional, para dados de teste mais realistas)
- OpenAI ou Transformers (opcional, para sugestões com IA)

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
# flask_auto_healer_universal
