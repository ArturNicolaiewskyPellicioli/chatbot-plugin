# Validação com volume projetado

O desenho só é aprovado depois de medido. Este roteiro roda em um Postgres local descartável.

## 1. Subir o banco

Com Docker (mesma versão maior do Postgres do PaaS):

```bash
docker run -d --name ciclo-pg -e POSTGRES_PASSWORD=dev -p 54329:5432 pgvector/pgvector:pg18
```

Se o usuário não usar Docker, Testcontainers no próprio teste de integração resolve o mesmo problema. Para usar o Postgres MCP Pro com sugestão de índices, o banco precisa das extensões `pg_stat_statements` e `hypopg`; se a imagem não tiver `hypopg`, pular essa parte.

## 2. Aplicar migrações do zero

Usar o comando de migração do ORM contra o banco local. Toda falha é bug da migração, não do ambiente.

## 3. Dados sintéticos

Gerar com `generate_series` o volume de 12 meses da descoberta (cenário provável) e, para as consultas mais críticas, o de 24 meses (cenário máximo). Exemplo de base:

```sql
-- partições para o período gerado (ou rodar o job de partições)
-- ...
INSERT INTO tenants (name) SELECT 'tenant ' || g FROM generate_series(1, 5) g;
-- contatos, contact_channels e conversas proporcionais à descoberta
-- mensagens: distribuir created_at ao longo dos meses, 60% inbound / 40% outbound
```

Gerar embeddings sintéticos aleatórios só para testar índice e plano; recall real se mede na fase 4 com embeddings verdadeiros.

Depois de carregar: `VACUUM (ANALYZE);`.

## 4. Consultas críticas

Medir com `EXPLAIN (ANALYZE, BUFFERS)` e registrar no documento: índice usado, linhas lidas, tempo. Conjunto mínimo:

| Consulta | O que comprovar |
|---|---|
| Gravar evento de webhook com `ON CONFLICT DO NOTHING` | usa a PK; tempo constante |
| Buscar ou criar `contact_channels` por telefone ou BSUID | índice único parcial |
| Janela de 24h (`last_inbound_at` do contact_channel) | leitura por PK |
| Últimas N mensagens da conversa, com keyset | `messages_timeline_idx`, poda de partições |
| Atualizar status por `provider_message_id` com filtro de 7 dias | poda de partições + índice |
| Reivindicar lote do outbox com `FOR UPDATE SKIP LOCKED` | índice parcial |
| kNN em `kb_chunks` filtrando por tenant (com varredura iterativa) | índice HNSW; quantidade de resultados correta |
| Busca híbrida (vetor + `tsvector`) com RRF | índices HNSW e GIN |
| Caixa de entrada do atendimento humano (`handoffs` abertos por tenant) | índice parcial |
| Custo de LLM por conversa no mês | índice de `llm_runs` |

Se uma consulta não usar índice ou ler muito mais linhas que retorna, voltar ao desenho.

## 5. Saúde

Com o Postgres MCP Pro em modo `restricted` apontado para este banco: `analyze_db_health`, `get_top_queries` (após rodar as consultas), `analyze_workload_indexes`. Tratar sugestões como hipóteses a confirmar com `EXPLAIN`, não como verdade.
