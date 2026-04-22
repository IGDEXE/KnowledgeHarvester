# KnowledgeHarvester

KnowledgeHarvester é uma ferramenta para **coleta, normalização e estruturação de documentação técnica a partir de fontes web**, com foco em uso automatizado via CLI e integração em pipelines CI/CD.

---

## 🧠 Conceito

A ferramenta percorre uma documentação online, extrai conteúdo relevante e gera uma base local estruturada em Markdown, pronta para:

* análise técnica
* comparação com documentação interna
* uso como contexto em LLMs
* construção de bases de conhecimento

Pipeline:

```text
crawl → clean → normalize → classify → chunk → store
```

---

## 📦 Saída gerada

```text
output/
├── raw/          # conteúdo bruto
├── structured/   # conteúdo com metadados
├── chunked/      # conteúdo dividido para consumo
```

---

## ▶️ Como usar (CLI)

O KnowledgeHarvester não depende de arquivos de configuração.
Toda a execução é feita via parâmetros.

### Execução básica

```bash
python knowledge_harvester.py \
  --base_url "<BASE_URL>" \
  --start_url "<START_URL>" \
  --link_filter "<FILTER>" \
  --keywords "<KEYWORDS>"
```

---

## ⚙️ Parâmetros

| Parâmetro       | Obrigatório | Descrição                                        |
| --------------- | ----------- | ------------------------------------------------ |
| `--base_url`    | ✔           | Domínio base da documentação                     |
| `--start_url`   | ✔           | URL inicial do crawl                             |
| `--link_filter` | ✖           | Filtra caminhos internos (ex: `/docs/`)          |
| `--keywords`    | ✖           | Lista separada por vírgula usada para relevância |
| `--max_pages`   | ✖           | Limite de páginas                                |
| `--delay`       | ✖           | Delay entre requests                             |
| `--min_score`   | ✖           | Score mínimo para incluir conteúdo               |

---

## 🧠 Relevância e classificação

A ferramenta utiliza:

* **keywords** → determinam se o conteúdo é relevante
* **classificação leve** → categorização baseada em termos

Exemplo de formato esperado:

```text
keyword1,keyword2,keyword3
```

---

## ✂️ Chunking

Os documentos são automaticamente divididos com base em seções (`##`), respeitando limites de tamanho para facilitar uso posterior em LLMs.

---

## ⚙️ Uso em CI/CD (GitHub Actions)

O projeto foi projetado para rodar diretamente em pipelines.

### Exemplo de execução no workflow

```yaml
- name: Run KnowledgeHarvester
  run: |
    python knowledge_harvester.py \
      --base_url "$BASE_URL" \
      --start_url "$START_URL" \
      --link_filter "$LINK_FILTER" \
      --keywords "$KEYWORDS"
```

---

## 🔐 Uso com Secrets

Recomendado utilizar variáveis protegidas:

```yaml
env:
  BASE_URL: ${{ secrets.BASE_URL }}
  START_URL: ${{ secrets.START_URL }}
  LINK_FILTER: ${{ secrets.LINK_FILTER }}
  KEYWORDS: ${{ secrets.KEYWORDS }}
```

---

## 🎯 Casos de uso

* Construção de base de conhecimento técnica
* Atualização de documentação interna
* Comparação entre fontes externas e conteúdo interno
* Preparação de dados para RAG
* Consulta offline de documentação

---

## ⚠️ Limitações

* Não realiza inferência semântica (sem LLM)
* Classificação baseada em regras simples
* Dependente da qualidade do HTML da fonte

---

## 🚀 Evolução

Possíveis melhorias:

* Diff entre execuções
* Indexação para busca local
* Suporte a múltiplos targets por execução
* Classificação configurável via CLI

---

## 📄 Licença

MIT License