# RAG para o chatbot

## Primeiro: precisa de RAG?

Se a base de conhecimento tem menos de cerca de 200 mil tokens, a Anthropic sugere colocá-la inteira no prompt com cache, sem recuperação ([Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)). É mais simples, não tem erro de recuperação e o cache reduz custo e latência. Reavaliar quando a base crescer.

## Quando precisa: Contextual Retrieval + híbrida + rerank

Resultados publicados pela Anthropic, em falhas de recuperação nos top-20 ([Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)):

| Técnica | Redução de falhas |
|---|---|
| Embeddings contextuais | 35% |
| + BM25 (busca lexical) | 49% |
| + rerank | 67% |

Como aplicar no modelo de dados (`kb_chunks`):
1. Dividir documentos em chunks; para cada um, gerar com um modelo pequeno 50 a 100 tokens de contexto ("este trecho é da política de trocas, seção prazos") e gravar em `context`.
2. Embedding de `context + content` em `embedding`; `tsv` (gerada) cobre a busca lexical em português.
3. Consulta: top-K vetorial (pgvector, HNSW) + top-K lexical (`tsv @@ websearch_to_tsquery('portuguese', ...)` com `ts_rank`), fundidos por Reciprocal Rank Fusion.
4. Rerank dos ~20 melhores com um modelo de rerank; enviar os 3 a 5 melhores ao modelo de resposta.
5. Citações: passar os trechos como blocos de documento ou `search_result` para o modelo citar a fonte ([citations](https://platform.claude.com/docs/en/build-with-claude/citations)).

## Embeddings e rerank

- A Anthropic não oferece modelo de embedding próprio e aponta a Voyage AI ([embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)). Alternativas comuns: OpenAI, Cohere. Escolher no ADR de IA com: qualidade em português, dimensão (limite do índice: `vector` 2.000, `halfvec` 4.000), preço, residência dos dados.
- Rerank: Voyage ([reranker](https://docs.voyageai.com/docs/reranker)) ou Cohere ([rerank](https://docs.cohere.com/docs/rerank-overview)). Conferir modelos atuais na data.
- Guardar `embedding_model` em cada chunk; trocar de modelo exige reindexar tudo.

## Ingestão

- `kb_documents.content_hash` evita reprocessar o que não mudou.
- Ingestão roda no worker, nunca na requisição.
- Remover chunks de documentos apagados (FK com `ON DELETE CASCADE`).
- Multi-tenant: todo chunk tem `tenant_id` e toda consulta filtra por ele (ver nota de varredura iterativa em `modelar-banco/references/modelo-referencia.md`).

## Medir recuperação

Antes de medir a resposta final, medir a recuperação: para cada pergunta do conjunto de evals, o chunk certo está entre os top-K? Recall@K e MRR por intenção. Ferramentas: skill `llm-evaluation` (llm-application-dev) ou asserções do promptfoo.
