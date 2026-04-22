# KnowledgeHarvester

KnowledgeHarvester é uma ferramenta para **coleta, normalização e estruturação de documentação técnica a partir de fontes web**.

O objetivo é transformar documentação online (HTML) em uma base local organizada, limpa e pronta para:

* análise técnica
* comparação com documentação interna
* uso como contexto em sistemas de IA
* construção de bases de conhecimento

---

## 🧠 Conceito

Documentação web normalmente apresenta:

* excesso de ruído (menus, navegação, scripts)
* fragmentação em múltiplas páginas
* dificuldade de reutilização programática

KnowledgeHarvester resolve isso através de um pipeline simples:

```text
crawl → clean → normalize → classify → chunk → store
```

---

## ⚙️ O que o projeto faz

* Navega automaticamente por uma documentação web
* Extrai apenas o conteúdo relevante
* Converte HTML para Markdown
* Remove elementos irrelevantes (UI, scripts, etc.)
* Deduplica conteúdo
* Classifica por categorias (configuráveis)
* Divide em chunks otimizados para consumo por LLMs
* Salva em estrutura organizada no disco

---

## 📂 Estrutura de saída

```text
output/
├── raw/          ← conteúdo bruto convertido
├── structured/   ← conteúdo com metadados
├── chunked/      ← conteúdo dividido por contexto
```

---

## ▶️ Como usar

### 1. Criar um arquivo de configuração

Exemplo (`veracode.json`):

```json
{
  "base_url": "https://docs.veracode.com",
  "start_url": "https://docs.veracode.com/r/c_about_veracode",
  "link_filter": "/r/",
  "keywords": ["scan", "api", "policy", "pipeline", "analysis"],
  "categories": {
    "sast": ["static analysis"],
    "dast": ["dynamic analysis"],
    "api": ["api"],
    "auth": ["authentication"]
  }
}
```

---

### 2. Executar o script

```bash
python knowledge_harvester.py --config veracode.json
```

---

## ⚙️ Parâmetros de configuração

| Campo         | Descrição                               |
| ------------- | --------------------------------------- |
| `base_url`    | Domínio base da documentação            |
| `start_url`   | Página inicial do crawl                 |
| `link_filter` | Filtro de URLs internas (opcional)      |
| `keywords`    | Termos usados para relevância           |
| `categories`  | Classificação baseada em palavras-chave |
| `max_pages`   | Limite de páginas (opcional)            |
| `delay`       | Delay entre requests (opcional)         |
| `min_score`   | Score mínimo para incluir página        |

---

## 🧠 Classificação e relevância

O projeto utiliza regras simples baseadas em texto:

* **score** → determina se o conteúdo é relevante
* **categorias** → definidas por palavras-chave

Exemplo:

```json
"categories": {
  "api": ["api", "endpoint"],
  "auth": ["authentication", "token"]
}
```

---

## ✂️ Chunking

Os documentos são automaticamente divididos em partes menores para:

* facilitar uso em LLMs
* melhorar recuperação de contexto
* evitar limites de contexto

---

## 🎯 Casos de uso

* Construção de base de conhecimento técnica
* Atualização de documentação interna
* Comparação entre versões de documentação
* Preparação de dados para RAG
* Consulta offline de documentação

---

## ⚠️ Limitações

* Não realiza inferência semântica (sem LLM)
* Classificação baseada em regras simples
* Pode exigir ajuste de `keywords` para melhor cobertura
* Não detecta mudanças entre execuções (ainda)

---

## 🚀 Roadmap

Possíveis evoluções:

* Diff entre execuções (detecção de mudanças)
* Comparação automática com CSV/documentação interna
* Busca local (TF-IDF / embeddings)
* Interface CLI mais completa
* Suporte a múltiplos targets em lote

---

## 📌 Filosofia

KnowledgeHarvester não tenta “entender” a documentação.

Ele atua como uma camada de:

* extração
* limpeza
* estruturação

O objetivo é **maximizar a utilidade do conteúdo para sistemas posteriores**.

---

## 📄 Licença

MIT License
