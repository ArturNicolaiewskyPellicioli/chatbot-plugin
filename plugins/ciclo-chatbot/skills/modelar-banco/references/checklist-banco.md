# Checklist de revisão do banco

Severidade: **B** bloqueia o portão · **A** alta, corrigir antes de produção · **M** média, registrar decisão.

## Integridade e modelo
- [B] Toda tabela de negócio tem `tenant_id NOT NULL` (ou decisão registrada de single-tenant definitivo).
- [B] Multi-tenant: relações entre tabelas de negócio usam FK composta `(tenant_id, x)` contra `UNIQUE (tenant_id, id)` do pai, para o banco recusar referência entre tenants ([PG: constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)).
- [B] Idempotência de webhook por constraint única em `(provider, provider_event_id)`; nenhuma deduplicação só em memória ou só no Redis. Fonte: [Meta: reenvios por até 7 dias](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/overview).
- [B] Identidade do contato aceita BSUID sem telefone, e o BSUID é reaproveitado entre números do mesmo portfólio. Fonte: [Meta: BSUID](https://developers.facebook.com/documentation/business-messaging/whatsapp/business-scoped-user-ids/).
- [B] Nenhuma credencial (token de acesso, app secret) em coluna.
- [A] Restrições no banco, não só na aplicação: `NOT NULL`, `CHECK`, `UNIQUE`, FKs.
- [A] Status de mensagem com transição só para frente, garantida na própria instrução `UPDATE` (ordem explícita dos estados; `failed` só a partir de `queued` ou `sent`).
- [A] Sem `ON DELETE CASCADE` em dados de conversa; eliminação por job explícito e ordenado.
- [M] Enums como `text` + `CHECK` (fácil de evoluir) ou tipo enum, com decisão registrada.
- [M] `jsonb` só para payload bruto e dados realmente sem esquema; documentos pequenos, porque qualquer update reescreve a linha inteira ([PG: JSON](https://www.postgresql.org/docs/current/datatype-json.html)).

## Tipos e chaves
- [A] `timestamptz`, `text`, `bigint`/identity ou `uuid`; sem `serial`, `varchar(n)` arbitrário, `money`, `timestamp` sem fuso ([PG wiki](https://wiki.postgresql.org/wiki/Don%27t_Do_This)).
- [A] UUID v7 (ou bigint) em vez de UUID v4 nas tabelas de alto volume ([RFC 9562](https://www.rfc-editor.org/rfc/rfc9562.html)).
- [M] Identificadores em minúsculas, sem aspas.

## Índices
- [B] Toda FK tem um índice não parcial que comece pelas colunas da FK ou pela sua coluna seletiva; o Postgres não cria automaticamente, e índice parcial não serve para a checagem ([PG: constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)).
- [B] Cada consulta crítica do documento tem um índice que a atende e o `EXPLAIN` comprova.
- [A] Linha do tempo da conversa com índice composto `(conversation_id, created_at DESC)`, limite inferior em `created_at` para podar partições e paginação por chave (keyset), nunca `OFFSET` ([Use The Index, Luke](https://use-the-index-luke.com/no-offset)).
- [A] Filas em tabela (`outbox`, `inbound_events` pendentes) com índice parcial `WHERE processed_at IS NULL` ([PG: índices parciais](https://www.postgresql.org/docs/current/indexes-partial.html)) e consumo com `FOR UPDATE SKIP LOCKED` ([PG: SELECT](https://www.postgresql.org/docs/current/sql-select.html)).
- [M] Sem índices redundantes (prefixo de outro índice) nem índices sem uso previsto.
- [M] Índices de cobertura (`INCLUDE`) só onde o `EXPLAIN` mostrar ganho de index-only scan.
- [M] BRIN em `created_at`/`received_at` para tabelas grandes só de inserção ([PG: BRIN](https://www.postgresql.org/docs/current/brin.html)).

## Escala
- [A] Projeção de tamanho em 12 e 24 meses por tabela, com a conta mostrada. Incluir `inbound_events` (cerca de uma linha por mensagem recebida mais até três por mensagem enviada).
- [A] Particionamento decidido com base na projeção. Se particionado: chaves únicas incluem a chave de partição; sem partição `DEFAULT` (ela impede `DETACH ... CONCURRENTLY`); job cria partições à frente com `ATTACH PARTITION` e alerta quando faltarem ([PG: particionamento](https://www.postgresql.org/docs/current/ddl-partitioning.html)).
- [A] Consultas de atualização de status filtram por janela de tempo para permitir poda de partições, com nova tentativa em janela maior quando nada for atualizado.
- [A] Pooling definido; migrações por conexão direta; nada que dependa de estado de sessão sob PgBouncer em modo transação ([PgBouncer](https://www.pgbouncer.org/features.html)).
- [A] Retenção por tabela definida e implementada (payload bruto de webhook com retenção curta, apagado em lotes ou por partição).

## pgvector
- [A] Tipo e dimensão compatíveis com o modelo de embedding e com o limite do índice (`vector` até 2.000, `halfvec` até 4.000 dimensões).
- [A] Estratégia de filtro por tenant definida (varredura iterativa, índice parcial ou partição) ([pgvector](https://github.com/pgvector/pgvector)).
- [A] Coluna com o nome do modelo de embedding e plano para troca de modelo (coluna nova + reindexação).
- [M] Busca híbrida (vetor + `tsvector`) se a descoberta indicar termos exatos (códigos, nomes de produtos).

## Segurança e LGPD
- [B] Se multi-tenant: RLS habilitado e forçado nas tabelas de negócio, com política que use `NULLIF(current_setting('app.tenant_id', true), '')::uuid`; aplicação conecta com papel sem `BYPASSRLS` e que não é dono das tabelas ([PG: RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)).
- [A] Tabelas de sistema sem RLS (`channel_accounts`, `inbound_events`, `message_status_events`, `outbox`) protegidas por `GRANT` por papel e documentadas.
- [A] Job de eliminação de titular testado de ponta a ponta: mensagens, fatos, consentimentos, chunks derivados, `llm_runs`, `tool_calls`, payloads brutos, mídia e traces ([LGPD arts. 16 e 18](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)).
- [A] Hash de telefone é pseudonimização, não anonimização (LGPD art. 13 §4º); não usar como argumento de anonimização.
- [A] Consentimentos só por inserção, com origem e evidência.

## Migrações
- Ver `migracoes-seguras.md`. Squawk sem alertas ou alerta justificado por escrito, inclusive em stacks cujas migrações não são `.sql` (rodar no SQL gerado).
