# KnowledgeHarvester

KnowledgeHarvester é uma ferramenta para **coleta, limpeza e consolidação de documentação técnica a partir de fontes web**, gerando uma base única estruturada e utilizável em projetos.

---

## 🧠 Conceito

A ferramenta percorre uma documentação online, extrai o conteúdo relevante (incluindo sites modernos com JavaScript) e gera **um único arquivo consolidado**, otimizado para consulta e uso programático.

Pipeline:

```text
crawl → render → clean → extract → filter → structure → consolidate
```

---

## 🎯 Objetivo

Gerar uma base de conhecimento que seja:

* consistente
* deduplicada
* navegável
* sem ruído de UI
* com contexto suficiente por seção

---

## ⚙️ Requisitos

* Python 3.11+
* Dependências no `requirements.txt`

Instalação:

```bash
pip install -r requirements.txt
playwright install
```

---

## ▶️ Uso (CLI)

Execução via parâmetros:

```bash
python knowledge_harvester.py \
  --base_url "<BASE_URL>" \
  --start_url "<START_URL>" \
  --keywords "<KEYWORDS>"
```

---

## ⚙️ Parâmetros

| Parâmetro       | Obrigatório | Descrição                                  |
| --------------- | ----------- | ------------------------------------------ |
| `--base_url`    | ✔           | Domínio base da documentação               |
| `--start_url`   | ✔           | URL inicial do crawl                       |
| `--keywords`    | ✖           | Lista separada por vírgula para relevância |
| `--link_filter` | ✖           | Restringe navegação por path               |
| `--max_pages`   | ✖           | Limite de páginas processadas              |
| `--min_score`   | ✖           | Score mínimo para incluir conteúdo         |

---

## 📦 Saída

A ferramenta gera **um único arquivo consolidado**:

```text
output/
└── knowledge_base.md
```

---

## 🧠 Estrutura do conteúdo

Cada página é organizada por seções:

```md
# <URL da página>

## <Seção>

conteúdo...

---

# <próxima página>
```

---

## 🔍 Processamento aplicado

Durante a execução:

* renderização completa via browser headless
* remoção de elementos de UI (menu, sidebar, etc.)
* extração do conteúdo principal
* normalização para Markdown
* remoção de duplicações
* filtragem por relevância
* agrupamento por página e seção

---

## ⚠️ Controle de escopo

Para evitar crescimento excessivo:

* o crawl é limitado por `max_pages`
* URLs duplicadas são ignoradas
* anchors (`#`) são descartados
* conteúdo pequeno é filtrado

---

## ⚙️ Uso em CI/CD

Exemplo de execução:

```yaml
- name: Run KnowledgeHarvester
  run: |
    python knowledge_harvester.py \
      --base_url "$BASE_URL" \
      --start_url "$START_URL" \
      --keywords "$KEYWORDS"
```

---

## 📦 Publicação de artefato

Não é necessário zip manual:

```yaml
- name: Upload artifact
  uses: actions/upload-artifact@v4
  with:
    name: knowledge-harvester-output
    path: output/
```

---

## 🚀 Características

* compatível com SPA (docs modernas)
* saída consolidada (sem fragmentação)
* deduplicação automática
* estrutura previsível
* pronto para uso direto em projetos

---

## ⚠️ Limitações

* consumo maior de recursos (uso de browser headless)
* depende da estrutura HTML da fonte
* não realiza análise semântica avançada

---

## 📄 Licença

MIT License
