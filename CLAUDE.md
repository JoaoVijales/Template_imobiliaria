# CLAUDE.md — Regras e Fluxo de Desenvolvimento

## Visão Geral do Projeto

Template de site para imobiliária desenvolvido com Django, seguindo boas práticas de engenharia de software, com painel administrativo personalizado e frontend moderno.

---

## Agentes Especializados

Este projeto utiliza agentes especializados que devem ser acionados conforme o contexto:

### 1. Code Writer Agent
- **Quando usar**: Implementação de novas features, modelos, views, templates
- **Responsabilidades**: Escrever código limpo, seguir padrões SOLID, aplicar Clean Code
- **Saída esperada**: Código funcional com docstrings, tipagem e testes unitários correspondentes

### 2. Review Agent
- **Quando usar**: Após cada feature ou pull request
- **Responsabilidades**: Revisar código para qualidade, legibilidade, aderência aos padrões
- **Checklist**: SOLID, DRY, KISS, nomes significativos, funções com responsabilidade única

### 3. QA Agent
- **Quando usar**: Antes de merge para branch principal
- **Responsabilidades**: Validar cobertura de testes, rodar suite de testes, verificar edge cases
- **Meta**: Cobertura mínima de 80% no código de negócio

### 4. Security Agent
- **Quando usar**: Antes de releases e ao introduzir novos endpoints/forms
- **Responsabilidades**: Verificar CSRF, XSS, SQL Injection, permissões, dados sensíveis expostos
- **Ferramentas**: bandit, django security checklist

---

## Fluxo Oficial de Desenvolvimento

```
1. PLAN     → Definir requisitos, criar/atualizar tickets
2. WRITE    → Code Writer Agent implementa a feature em branch feature/*
3. TEST     → QA Agent valida testes (TDD: testes antes do código)
4. REVIEW   → Review Agent analisa qualidade e padrões
5. SECURITY → Security Agent valida antes do merge
6. MERGE    → PR para develop após aprovações
7. RELEASE  → develop → main com tag semântica
```

### Branches
```
main          → produção, protegida
develop       → integração, testes passando
feature/*     → novas features
fix/*         → correções de bugs
hotfix/*      → correções urgentes em produção
```

### Commits (Conventional Commits)
```
feat: adiciona listagem de imóveis com filtros
fix: corrige cálculo de área útil
test: adiciona testes para PropertyRepository
refactor: extrai lógica de busca para SearchService
docs: atualiza README com instruções de deploy
style: formata arquivos com black e isort
```

---

## Princípios de Código

### TDD (Test-Driven Development)
1. **Red**: Escrever teste que falha
2. **Green**: Implementar código mínimo para passar
3. **Refactor**: Melhorar sem quebrar testes

### SOLID
- **S** — Single Responsibility: Cada classe/função tem uma única razão para mudar
- **O** — Open/Closed: Aberto para extensão, fechado para modificação
- **L** — Liskov Substitution: Subtipos substituíveis por seus tipos base
- **I** — Interface Segregation: Interfaces específicas melhor que uma geral
- **D** — Dependency Inversion: Depender de abstrações, não de implementações

### Clean Code
- Nomes descritivos e sem abreviações obscuras
- Funções pequenas com responsabilidade única (≤ 20 linhas idealmente)
- Sem comentários óbvios; comentários apenas para "por quê", não "o quê"
- Sem código morto ou comentado
- Máximo 3 parâmetros por função; use dataclasses/DTOs para mais

### Django Específico
- Fat Models, Thin Views — lógica de negócio nos models/services
- Repository Pattern para acesso a dados
- Service Layer para lógica de negócio complexa
- Forms para validação de entrada
- Signals apenas quando necessário e documentados

---

## Estrutura do Projeto

```
Template_imobiliaria/
├── manage.py
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── setup.cfg
├── .env.example
├── CLAUDE.md
├── config/                    # Configurações Django
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/                  # App principal (homepage, sobre, contato)
│   ├── properties/            # App de imóveis
│   └── accounts/              # App de usuários (opcional)
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── base.html
│   ├── core/
│   ├── properties/
│   └── admin/                 # Templates customizados do admin
├── media/                     # Uploads (gitignored)
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

---

## Padrões de Teste

```python
# Nomenclatura de testes
class TestPropertyModel:
    def test_should_calculate_price_per_sqm_correctly(self): ...
    def test_should_return_featured_properties_only(self): ...

class TestPropertyListView:
    def test_should_display_active_properties(self): ...
    def test_should_filter_by_city_when_provided(self): ...
```

---

## Comandos Úteis

```bash
# Instalar dependências
pip install -r requirements-dev.txt

# Rodar testes
pytest --cov=apps --cov-report=html

# Verificar segurança
bandit -r apps/

# Formatação
black apps/ && isort apps/

# Lint
flake8 apps/

# Rodar servidor
python manage.py runserver --settings=config.settings.development
```

---

## Checklist de PR

- [ ] Testes escritos antes do código (TDD)
- [ ] Cobertura ≥ 80% no código novo
- [ ] Sem warnings de segurança (bandit)
- [ ] Código formatado (black + isort)
- [ ] Lint sem erros (flake8)
- [ ] Migrations geradas e testadas
- [ ] Admin registrado para novos modelos
- [ ] Documentação atualizada se necessário
