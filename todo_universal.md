# Tarefas para o Agente Flask Autocurador Supremo Universal

## Análise e Planejamento
- [x] Confirmar requisitos com o usuário
- [x] Analisar o script existente e identificar componentes principais
- [ ] Planejar estrutura universal e independente de projeto específico
- [ ] Definir heurísticas para detecção automática de estrutura Flask

## Implementação da Versão Universal
- [ ] Implementar detecção automática de diretórios (templates, static, routes, models)
- [ ] Criar sistema de reconhecimento do núcleo do app Flask (create_app, Flask(__name__))
- [ ] Adaptar para compatibilidade com diferentes modelos de projeto
- [ ] Implementar suporte a diferentes bancos de dados e sistemas de autenticação
- [ ] Desenvolver detecção automática de padrões e endpoints
- [ ] Eliminar suposições específicas e valores hardcoded
- [ ] Criar fallbacks inteligentes para componentes ausentes

## CLI Universal e Relatórios
- [ ] Implementar CLI universal com novas opções (--auto-detect, --blueprint-aware, etc.)
- [ ] Adicionar suporte a presets (blog, ecommerce, admin-panel)
- [ ] Desenvolver sistema de exportação de relatórios em múltiplos formatos
- [ ] Implementar geração de diagnostic_bundle.zip

## Integração e Distribuição
- [ ] Criar sistema de plugabilidade para integração com outros projetos
- [ ] Desenvolver template para GitHub Actions
- [ ] Implementar setup.py para instalação global
- [ ] Preparar documentação para uso em múltiplos repositórios

## Testes e Finalização
- [ ] Testar em múltiplos modelos de projeto Flask
- [ ] Validar compatibilidade com diferentes estruturas
- [ ] Gerar relatórios finais e documentação
- [ ] Entregar versão universal ao usuário
