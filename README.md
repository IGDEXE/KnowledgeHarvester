# KnowledgeHarvester

KnowledgeHarvester é uma ferramenta para **coleta, normalização e estruturação de documentação técnica a partir de fontes web**, projetada para funcionar tanto localmente quanto em pipelines CI/CD.

---

## 🧠 Conceito

O projeto percorre uma documentação online, extrai conteúdo relevante (inclusive de sites modernos com JavaScript) e gera uma base estruturada pronta para uso em:

* análise técnica
* comparação com documentação interna
* sistemas de IA (RAG / contexto)
* consulta offline

Pipeline:

```text
crawl → render → extract → normalize → classify → chunk → store
```

---

## ⚙️ Requisitos

* Python 3.11+
* Dependências definidas em `requirements.txt`

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
| `--base_url`    | ✔           | Domínio base                               |
| `--start_url`   | ✔           | URL inicial                                |
| `--keywords`    | ✖           | Lista separada por vírgula para relevância |
| `--link_filter` | ✖           | Restringe navegação por path               |
| `--max_pages`   | ✖           | Limite de páginas                          |
| `--min_score`   | ✖           | Score mínimo para inclusão                 |

---

## 📂 Estrutura de saída

```text
output/
├── raw/          # conteúdo bruto em Markdown
├── structured/   # conteúdo com metadados
├── chunked/      # conteúdo dividido para LLM
```

---

## 🧠 Relevância

O sistema usa keywords para determinar importância:

* cada ocorrência aumenta o score
* páginas abaixo do threshold são descartadas

---

## ✂️ Chunking

Os documentos são divididos automaticamente para:

* evitar limites de contexto
* facilitar recuperação de informação
* melhorar uso em LLMs

---

## ⚙️ Uso em CI/CD (GitHub Actions)

### Execução do script

```yaml
- name: Run KnowledgeHarvester
  run: |
    python knowledge_harvester.py \
      --base_url "$BASE_URL" \
      --start_url "$START_URL" \
      --keywords "$KEYWORDS"
```

---

## 🔐 Configuração via Secrets

Recomendado usar variáveis protegidas:

```yaml
env:
  BASE_URL: ${{ secrets.BASE_URL }}
  START_URL: ${{ secrets.START_URL }}
  KEYWORDS: ${{ secrets.KEYWORDS }}
```

---

## 📦 Publicação de artefatos

⚠️ **Importante:** não é necessário criar zip manualmente.

O GitHub Actions já faz isso automaticamente:

```yaml
- name: Upload artifact
  uses: actions/upload-artifact@v4
  with:
    name: knowledge-harvester-output
    path: output/
```

---

## 🚀 Características importantes

* Compatível com sites modernos (SPA) via browser headless
* Estrutura otimizada para uso com LLM
* Pipeline automatizável
* Configuração via CLI (sem arquivos estáticos)

---

## ⚠️ Limitações

* Pode consumir mais recursos por usar browser headless
* Crawl não é infinito (controlado por `max_pages`)
* Qualidade depende da estrutura do site

---

## 📄 Licença

MIT License
